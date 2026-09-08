"""Durable review decisions over immutable extraction and claim revisions."""

from __future__ import annotations

from copy import deepcopy
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

from jsonschema import ValidationError
from rulespec_projection.attestations import attestation_row, parse_targets
from rulespec_projection.projection import OffsetVerificationError, verify_fragment
from rulespec_projection.provenance import RunContext

from .core import SCHEMA_VERSION, MEANING_FIELDS, build_graph, canonical, evidence_expectations, resolve_links, revise_claim


class ReviewError(ValueError):
    """A review request cannot be applied."""


class RevisionConflict(ReviewError):
    """Another review action changed the run before this request arrived."""

    def __init__(self, expected: int, current: int) -> None:
        self.expected = expected
        self.current = current
        super().__init__(f"This run changed from revision {expected} to {current}. Reload before saving.")


class ReviewIntegrityError(ReviewError):
    """The pinned extraction or stored review history has changed."""


_CANDIDATE_FIELDS = frozenset({
    "kind", "summary", "actor", "quote", "start", "end", "action", "object",
    "actor_quote", "action_quote", "object_quote", "logic_text", "relation",
    "applies_to", "references", "section_id", *MEANING_FIELDS,
})
_ACTIONS = frozenset({"add", "edit", "split", "merge", "approve", "reject"})
_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (
    sequence INTEGER PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    payload TEXT NOT NULL,
    previous_sha256 TEXT NOT NULL,
    event_sha256 TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
BEGIN SELECT RAISE(ABORT, 'Review events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
BEGIN SELECT RAISE(ABORT, 'Review events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS metadata_no_update BEFORE UPDATE ON metadata
BEGIN SELECT RAISE(ABORT, 'Review metadata is immutable'); END;
CREATE TRIGGER IF NOT EXISTS metadata_no_delete BEFORE DELETE ON metadata
BEGIN SELECT RAISE(ABORT, 'Review metadata is immutable'); END;
"""


def _sha(value: str | bytes) -> str:
    return hashlib.sha256(value.encode("utf-8") if isinstance(value, str) else value).hexdigest()


def _assertion_ids(claim: dict[str, Any]) -> list[str]:
    identities = claim.get("assertion_ids", [])
    if not isinstance(identities, list) or not identities or any(
        not isinstance(identity, str) or not identity for identity in identities
    ):
        raise ReviewIntegrityError("A claim is missing its component assertion identities.")
    if len(set(identities)) != len(identities):
        raise ReviewIntegrityError("A claim repeats a component assertion identity.")
    return identities


class ReviewStore:
    """Keep review history separately from the original extraction files.

    Each SQLite transaction compares the expected sequence, validates the action,
    and appends its full result. Reopening replays those saved results; it never
    asks a model or reruns a correction against changed source text.
    """

    def __init__(self, run_dir: str | Path) -> None:
        self.run_dir = Path(run_dir).resolve()
        if not self.run_dir.is_dir():
            raise ReviewError("The extraction run directory does not exist.")
        self.path = self.run_dir / "review.sqlite3"
        if self.path.is_symlink():
            raise ReviewIntegrityError("The review database must be a file inside this run.")
        self._base_bytes: dict[str, bytes] = {}
        values: dict[str, Any] = {}
        for name in ("document.json", "run.json", "rulebook.json"):
            try:
                content = (self.run_dir / name).read_bytes()
                values[name] = json.loads(content)
            except (OSError, ValueError) as exc:
                raise ReviewIntegrityError(f"Cannot read the original {name}.") from exc
            if not isinstance(values[name], dict):
                raise ReviewIntegrityError(f"The original {name} must contain an object.")
            self._base_bytes[name] = content
        self.document = values["document.json"]
        self.run = values["run.json"]
        self.base = values["rulebook.json"]
        self._manifest_required = (self.run_dir / "manifest.json").exists() or bool(self.run.get("manifest_file"))
        self._verify_extraction_manifest()
        text = self.document.get("text")
        if not isinstance(text, str) or self.document.get("sha256") != _sha(text):
            raise ReviewIntegrityError("The document text does not match its saved fingerprint.")
        embedded = self.base.get("document", {})
        if isinstance(embedded, dict) and embedded.get("text", text) != text:
            raise ReviewIntegrityError("The rulebook and document contain different source text.")
        base_claims = self.base.get("accepted")
        if not isinstance(base_claims, list):
            raise ReviewIntegrityError("The original rulebook has no accepted claim list.")
        identities = [claim.get("id") for claim in base_claims if isinstance(claim, dict)]
        if len(identities) != len(base_claims) or any(not isinstance(i, str) or not i for i in identities):
            raise ReviewIntegrityError("Every claim needs an immutable revision identity.")
        if len(set(identities)) != len(identities):
            raise ReviewIntegrityError("The original rulebook repeats a revision identity.")
        # Verify the supplied records before creating a database that pins them.
        # A self-consistent graph is a structural check, not a semantic approval.
        self._validated_graph(base_claims, [])
        self._fingerprints = {name: _sha(content) for name, content in self._base_bytes.items()}
        with closing(self._connect()) as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript(_DB_SCHEMA)
            connection.execute("BEGIN IMMEDIATE")
            metadata = dict(connection.execute("SELECT key, value FROM metadata"))
            if not metadata:
                connection.executemany("INSERT INTO metadata(key, value) VALUES (?, ?)", [
                    ("schema_version", "1"),
                    ("base_sha256", canonical(self._fingerprints)),
                ])
            elif metadata.get("schema_version") != "1" or metadata.get("base_sha256") != canonical(self._fingerprints):
                raise ReviewIntegrityError("The extraction differs from the version pinned by this review.")
            connection.commit()

    def _verify_extraction_manifest(self) -> None:
        manifest_path = self.run_dir / "manifest.json"
        if not self._manifest_required and not manifest_path.exists():
            return
        if manifest_path.is_symlink():
            raise ReviewIntegrityError("The extraction manifest must be a file inside this run.")
        # Viewing checks frozen artifacts, without requiring today's runtime to
        # match the extraction runtime or invoking a provider.
        from .extraction import _verify_manifest
        try:
            manifest = _verify_manifest(self.run_dir)
            for name, content in self._base_bytes.items():
                if manifest["artifacts_sha256"].get(name) != _sha(content):
                    raise ValueError(f"The loaded {name} differs from the manifest.")
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            raise ReviewIntegrityError(f"The extraction manifest failed verification: {exc}") from exc

    def _validate_evidence(self, claim: dict[str, Any]) -> None:
        evidence = claim.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise ReviewIntegrityError("A saved claim is missing its exact source evidence.")
        expected = evidence_expectations(claim)
        fields = set()
        artifact = SimpleNamespace(raw_fields={"text": self.document["text"]})
        for item in evidence:
            if not isinstance(item, dict):
                raise ReviewIntegrityError("Saved source evidence must contain evidence records.")
            field, quote = item.get("field"), item.get("quote")
            start, end = item.get("start"), item.get("end")
            if (not isinstance(field, str) or field not in expected or field in fields
                    or not isinstance(quote, str) or not quote or quote != expected[field]
                    or type(start) is not int or type(end) is not int or start >= end):
                raise ReviewIntegrityError("Saved source evidence disagrees with its claim content or source positions.")
            if field == "summary" and (start != claim.get("start") or end != claim.get("end")):
                raise ReviewIntegrityError("The main source evidence differs from the claim's source positions.")
            try:
                verified = verify_fragment(artifact, key=field, source_field="text", start=start, end=end,
                                           artifact_iri=self.document["id"], expected_text=quote)
            except (OffsetVerificationError, ValueError, TypeError, KeyError) as exc:
                raise ReviewIntegrityError("Saved source evidence does not match the pinned document.") from exc
            if item.get("fragment_id") != verified.urn:
                raise ReviewIntegrityError("A source evidence fragment has an inconsistent immutable identity.")
            fields.add(field)
        if "summary" not in fields:
            raise ReviewIntegrityError("A saved claim is missing its main source evidence.")
        issues = claim.get("issues", [])
        if not isinstance(issues, list):
            raise ReviewIntegrityError("Saved claim issues must be a list.")
        for field in ("actor", "action", "object"):
            if claim.get(field) and field not in fields and not any(
                isinstance(issue, dict) and issue.get("code") == "component_evidence_unresolved"
                and issue.get("field") == field for issue in issues
            ):
                raise ReviewIntegrityError("A claim component has neither exact evidence nor an explicit evidence issue.")
        for field in expected.keys() - {"summary", "actor", "action", "object", "logic_text"}:
            if field == "modality" and claim.get("modality") in {"not_stated", "uncertain"} and not expected[field]:
                continue
            if field not in fields and not any(isinstance(issue, dict)
                    and issue.get("code") == "component_evidence_unresolved"
                    and issue.get("field") == field for issue in issues):
                raise ReviewIntegrityError("A meaning component has neither evidence nor an explicit unresolved issue.")

    def _validated_graph(self, claims: list[dict[str, Any]], attestations: list[dict[str, Any]]) -> dict[str, Any]:
        for claim in claims:
            _assertion_ids(claim)
            self._validate_evidence(claim)
        rebuilt = deepcopy(claims)
        try:
            graph = build_graph(self.document, rebuilt, self.run, attestations=deepcopy(attestations))
        except (ValueError, TypeError, KeyError) as exc:
            raise ReviewIntegrityError("The saved claims or attestations cannot be rebuilt consistently.") from exc
        for supplied, checked in zip(claims, rebuilt, strict=True):
            if set(_assertion_ids(supplied)) != set(_assertion_ids(checked)):
                raise ReviewIntegrityError("Saved claim content disagrees with its immutable component assertion identities.")
        assertion_ids = {node["@id"] for node in graph["@graph"]
                         if node.get("@type") in {"rkaf:ValueAssertion", "rkaf:RelationshipAssertion"}}
        for claim in claims:
            if not set(_assertion_ids(claim)) <= assertion_ids:
                raise ReviewIntegrityError("A claim component assertion is missing from the retained graph.")
        for row in attestations:
            try:
                targets = parse_targets(row.get("rkaf:targets") if row.get("@type") == "rkaf:Attestation"
                                        else row.get("target_ids_json"))
            except ValueError as exc:
                raise ReviewIntegrityError("A saved review attestation has invalid assertion targets.") from exc
            if not set(targets) <= assertion_ids:
                raise ReviewIntegrityError("A review attestation target is missing from the retained assertion graph.")
        return graph

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10, isolation_level=None)
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    def _check_base(self) -> None:
        for name, fingerprint in self._fingerprints.items():
            try:
                matches = _sha((self.run_dir / name).read_bytes()) == fingerprint
            except OSError as exc:
                raise ReviewIntegrityError(f"The original {name} is missing.") from exc
            if not matches:
                raise ReviewIntegrityError(f"The original {name} changed. Review requires the pinned extraction.")
        self._verify_extraction_manifest()

    def _read_events(self, connection: sqlite3.Connection) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        previous = _sha(canonical(self._fingerprints))
        for sequence, event_id, payload, saved_previous, saved_hash in connection.execute(
            "SELECT sequence, event_id, payload, previous_sha256, event_sha256 FROM events ORDER BY sequence"
        ):
            if sequence != len(result) + 1 or saved_previous != previous or _sha(previous + "\n" + payload) != saved_hash:
                raise ReviewIntegrityError("The saved review event history failed its integrity check.")
            try:
                event = json.loads(payload)
            except ValueError as exc:
                raise ReviewIntegrityError("A saved review event is unreadable.") from exc
            if not isinstance(event, dict) or event.get("id") != event_id or event.get("sequence") != sequence:
                raise ReviewIntegrityError("A saved review event has inconsistent identity.")
            result.append(event)
            previous = saved_hash
        return result

    def _state(self, events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
        revisions = deepcopy(self.base["accepted"])
        current = {claim["id"]: claim for claim in revisions}
        review: dict[str, dict[str, Any]] = {}
        known = set(current)
        for event in events:
            if event["action"] not in _ACTIONS or any(target not in current for target in event["targets"]):
                raise ReviewIntegrityError("A saved action targets a claim that was already replaced.")
            details = {key: deepcopy(event[key]) for key in ("actor", "actor_kind", "at", "rationale")}
            details["event_id"] = event["id"]
            if event["action"] in {"add", "edit", "split", "merge"}:
                if event["action"] == "add" and (event["targets"] or event["assertion_targets"]):
                    raise ReviewIntegrityError("A saved addition cannot replace an existing claim.")
                for target in event["targets"]:
                    current.pop(target)
                    review[target] = {**details, "status": "superseded", "replaced_by": [c["id"] for c in event["replacements"]]}
                for claim in deepcopy(event["replacements"]):
                    if event["action"] == "add" and ("supersedes" in claim or "prior_assertion_ids" in claim):
                        raise ReviewIntegrityError("A saved addition cannot invent a predecessor.")
                    if claim["id"] in known:
                        raise ReviewIntegrityError("A saved correction reuses an existing revision identity.")
                    known.add(claim["id"])
                    revisions.append(claim)
                    current[claim["id"]] = claim
            else:
                for target in event["targets"]:
                    review[target] = {**details, "status": "approved" if event["action"] == "approve" else "rejected"}
        return revisions, current, review

    def _snapshot(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        revisions, current, decisions = self._state(events)
        attestations = [deepcopy(row) for event in events for row in event.get("attestations", [])]
        graph = self._validated_graph(revisions, attestations)
        for claim in revisions:
            claim["review"] = deepcopy(decisions.get(claim["id"], {"status": "pending"}))
            claim["review_status"] = claim["review"]["status"]
        current_claims = [deepcopy(claim) for claim in revisions if claim["id"] in current]
        effective = [claim for claim in current_claims if claim["review_status"] != "rejected"]
        saved_targets = {claim["id"]: list(claim.get("target_ids", [])) for claim in current_claims}
        unresolved = resolve_links(self.document, effective)
        active_ids = {claim["id"] for claim in effective}
        for claim in current_claims:
            claim["link_issues"] = [deepcopy(issue) for issue in unresolved if issue["claim_id"] == claim["id"]]
            old_targets = saved_targets[claim["id"]]
            if set(old_targets) != set(claim.get("target_ids", [])) or any(target not in active_ids for target in old_targets):
                issue = {
                    "claim_id": claim["id"], "code": "qualification_target_changed", "field": "applies_to",
                    "message": "Affected rules changed. Edit this qualification to confirm its current rules.",
                    "previous_targets": old_targets, "candidate_targets": list(claim.get("target_ids", [])),
                }
                unresolved.append(issue)
                claim["link_issues"].append(deepcopy(issue))
                claim["target_ids"] = []
        counts = {status: sum(c["review_status"] == status for c in current_claims) for status in ("pending", "approved", "rejected")}
        current_issues = [{"claim_id": c["id"], "issues": deepcopy(c.get("issues", []) + c.get("link_issues", []))}
                          for c in current_claims if c.get("issues") or c.get("link_issues")]
        return {
            **deepcopy(self.base),
            "accepted": [c for c in current_claims if c["review_status"] != "rejected"],
            "rejected": deepcopy(self.base.get("rejected", [])) + [c for c in current_claims if c["review_status"] == "rejected"],
            "graph": graph,
            "unresolved": unresolved,
            "revision": len(events),
            "history": deepcopy(events),
            "attestations": attestations,
            "current": current_claims,
            "revisions": revisions,
            "current_issues": current_issues,
            "review_summary": {
                **counts,
                "total": len(current_claims),
                "claims_with_issues": len(current_issues),
                "status": "needs_review" if counts["pending"] else "decisions_recorded" if current_claims else "no_claims",
                "usage": "review_only",
                "scope": "Meaning and evidence of the targeted claim components; no operational authorization.",
            },
        }

    def snapshot(self) -> dict[str, Any]:
        """Return the effective rulebook, all revisions, and the complete history."""
        with closing(self._connect()) as connection:
            connection.execute("BEGIN")
            self._check_base()
            return self._snapshot(self._read_events(connection))

    def apply(self, action_dict: dict[str, Any]) -> dict[str, Any]:
        """Validate and append one action, or leave the run entirely unchanged."""
        return self._apply(action_dict, persist=True)

    def preview(self, action_dict: dict[str, Any]) -> dict[str, Any]:
        """Validate a correction through the real path without saving its event."""
        return self._apply(action_dict, persist=False)

    def _apply(self, action_dict: dict[str, Any], *, persist: bool) -> dict[str, Any]:
        request = self._validate_request(action_dict)
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            self._check_base()
            events = self._read_events(connection)
            if request["expected_revision"] != len(events):
                raise RevisionConflict(request["expected_revision"], len(events))
            _, current, decisions = self._state(events)
            if any(target not in current for target in request["targets"]):
                raise ReviewError("A target is missing or has been replaced. Select its current revision.")
            originals = [current[target] for target in request["targets"]]
            assertion_targets = list(dict.fromkeys(identity for claim in originals for identity in _assertion_ids(claim)))
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            event_id = "urn:rulespec:review-event:" + str(uuid4())
            attestor_id = "urn:rulespec:reviewer:" + _sha(request["actor_kind"] + ":" + request["actor"])
            event: dict[str, Any] = {
                "id": event_id,
                "sequence": len(events) + 1,
                "action": request["action"],
                "actor": request["actor"],
                "actor_kind": request["actor_kind"],
                "attestor_id": attestor_id,
                "rationale": request["rationale"],
                "at": now,
                "targets": request["targets"],
                "assertion_targets": assertion_targets,
                "replacement_fields": request.get("replacements", []),
                "replacements": [],
                "attestations": [],
            }
            if request["action"] in {"add", "edit", "split", "merge"}:
                for index, fields in enumerate(request["replacements"]):
                    original = ({"id": f"{event_id}:new:{index}", "assertion_ids": []}
                                if request["action"] == "add" else deepcopy(originals[0]))
                    if request["action"] != "edit":
                        original["rule_id"] = "urn:rulespec:rule:" + _sha(f"{event_id}:{index}")
                    try:
                        replacement = revise_claim(
                            self.document, original, fields, f"{event_id}:{index}",
                            origin="humanAsserted" if request["actor_kind"] == "humanUser" else "aiSuggested",
                        )
                    except (TypeError, ValueError, ValidationError) as exc:
                        raise ReviewError(f"The correction could not be saved: {exc}") from exc
                    if request["action"] == "add":
                        replacement.pop("supersedes", None)
                        replacement.pop("prior_assertion_ids", None)
                    else:
                        replacement["supersedes"] = list(request["targets"])
                        replacement["prior_assertion_ids"] = assertion_targets
                    _assertion_ids(replacement)
                    event["replacements"].append(replacement)
                # Resolve the new revisions against current, non-rejected claims.
                # Older revisions keep the links they originally asserted.
                active = [deepcopy(claim) for identity, claim in current.items()
                          if identity not in request["targets"] and decisions.get(identity, {}).get("status") != "rejected"]
                resolve_links(self.document, active + event["replacements"])
                # The Core builder adds any qualification assertion identities.
                build_graph(self.document, event["replacements"], self.run)
            else:
                row = attestation_row(
                    attestor_id=attestor_id,
                    attestor_kind="rkaf:" + request["actor_kind"],
                    targets=assertion_targets,
                    decision="rkaf:approved" if request["action"] == "approve" else "rkaf:rejected",
                    attestation_scope=(self.run.get("profile", SCHEMA_VERSION) + ": meaning and exact evidence; review only; "
                                       "no operational authorization; claim revisions=" + canonical(request["targets"])),
                    context=RunContext(run_id=event_id, asserted_at=now),
                    attested_at=now,
                    rationale=request["rationale"],
                )
                event["attestations"].append(row)
            snapshot = self._snapshot([*events, event])
            if not persist:
                connection.rollback()
                return snapshot
            payload = canonical(event)
            last = connection.execute("SELECT event_sha256 FROM events ORDER BY sequence DESC LIMIT 1").fetchone()
            previous = last[0] if last else _sha(canonical(self._fingerprints))
            connection.execute(
                "INSERT INTO events(sequence, event_id, payload, previous_sha256, event_sha256) VALUES (?, ?, ?, ?, ?)",
                (event["sequence"], event_id, payload, previous, _sha(previous + "\n" + payload)),
            )
            connection.commit()
            return snapshot

    @staticmethod
    def _validate_request(value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ReviewError("A review action must be a JSON object.")
        allowed = {"expected_revision", "actor", "actor_kind", "action", "targets", "rationale", "replacements"}
        if set(value) - allowed:
            raise ReviewError("The review action contains unsupported fields.")
        request = deepcopy(value)
        if type(request.get("expected_revision")) is not int or request["expected_revision"] < 0:
            raise ReviewError("Supply the revision you reviewed before saving.")
        if not isinstance(request.get("action"), str) or request["action"] not in _ACTIONS:
            raise ReviewError("Choose add, edit, split, merge, approve, or reject.")
        if not isinstance(request.get("actor_kind"), str) or request["actor_kind"] not in {"humanUser", "aiAgent"}:
            raise ReviewError("Identify the reviewer as a human user or an AI agent.")
        for key, limit in (("actor", 200), ("rationale", 10000)):
            if not isinstance(request.get(key), str) or not request[key].strip() or len(request[key]) > limit:
                raise ReviewError(f"Supply a non-empty {key} of at most {limit} characters.")
            request[key] = request[key].strip()
        targets = request.get("targets")
        action = request["action"]
        if action == "add" and targets != []:
            raise ReviewError("Adding a rule requires an empty target list; it does not replace existing claims.")
        if not isinstance(targets, list) or not (0 if action == "add" else 1) <= len(targets) <= 100 or any(not isinstance(t, str) or not t for t in targets):
            raise ReviewError("Select between 1 and 100 claim revisions.")
        if len(set(targets)) != len(targets):
            raise ReviewError("Select each claim revision only once.")
        if action in {"edit", "split"} and len(targets) != 1:
            raise ReviewError("Editing or splitting requires exactly one claim.")
        if action == "merge" and len(targets) < 2:
            raise ReviewError("Merging requires at least two claims.")
        if action in {"approve", "reject"}:
            if "replacements" in request:
                raise ReviewError("A decision cannot change the text or evidence of a claim.")
        else:
            replacements = request.get("replacements")
            if not isinstance(replacements, list) or any(not isinstance(item, dict) or not item for item in replacements):
                raise ReviewError("Supply the replacement claim fields.")
            if action == "split" and not 2 <= len(replacements) <= 20:
                raise ReviewError("Split a claim into between 2 and 20 replacements.")
            if action == "add" and not 1 <= len(replacements) <= 20:
                raise ReviewError("Add between 1 and 20 new rules.")
            if action in {"edit", "merge"} and len(replacements) != 1:
                raise ReviewError("Editing or merging requires exactly one replacement.")
            for fields in replacements:
                if set(fields) - _CANDIDATE_FIELDS:
                    raise ReviewError("Change claim content and evidence through the editable fields; identities and origins are fixed.")
                if action == "add" and not {"kind", "summary", "actor", "quote"} <= fields.keys():
                    raise ReviewError("A new rule needs its kind, meaning, actor, and exact source quotation.")
        try:
            canonical(request)
        except (TypeError, ValueError) as exc:
            raise ReviewError("The review action must contain finite JSON values.") from exc
        if action == "add" and len({canonical(fields) for fields in request["replacements"]}) != len(request["replacements"]):
            raise ReviewError("The same new rule appears more than once in this action.")
        return request
