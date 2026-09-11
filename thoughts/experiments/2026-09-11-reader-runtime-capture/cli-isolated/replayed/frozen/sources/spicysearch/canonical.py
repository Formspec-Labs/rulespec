"""Deterministic JSON, digests, and identifiers for SpicySearch product data.

The shared artifact protocol uses the installed Rulespec implementation. This
module remains for non-artifact search data, reports, and local identifiers.
"""

from __future__ import annotations

import functools
import hashlib
import json
import re
import secrets
import struct
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any


class IntegrityError(ValueError):
    """Raised when a digest, identifier, pin, or release shape check fails."""


class InvalidRequestError(IntegrityError):
    """Raised when a structurally valid request names unsupported runtime state."""


class ServingLimitError(Exception):
    """Raised when a bounded serving surface cannot fit a response, even
    after best-effort truncation, within its own byte or cost budget.

    Deliberately *not* an :class:`IntegrityError` subclass: an artifact that
    fails an integrity check disagrees with its own seal, while this means
    the served state is genuine and correctly verified, just too large to
    return from one bounded backstop. Routing both through the same code
    teaches every reader to distrust a genuine integrity refusal -- see the
    2026-09-06 ``GET /v1/facets`` defect this type exists to keep from
    recurring: a per-request result-size limit was raising
    :class:`IntegrityError` and reaching users as ``search_integrity_failure``
    on every real corpus, while the demo fixture's two-agency corpus never
    exercised the bound at all.

    **Load-bearing and easy to miss:** unlike the ``IntegrityError`` branch
    (``api/router.py``'s ``search_integrity_failure``, which discards
    ``str(error)`` in favor of one static literal precisely so an unclassified
    integrity failure can never leak anything the exception happened to be
    carrying), the router answers this type's own code (for example
    ``search_size_limit``) with ``str(error)`` verbatim, reaching an
    unauthenticated client exactly as written. Every raise site must keep
    this message a static string literal with no interpolation of anything
    corpus-, request-, or artifact-derived -- a bound's own configured value
    is fine (it is a fact about the service, not the corpus; see
    ``ServingLimitError``'s own message text throughout this codebase for the
    pattern), but a count, an id, or a path is not. This asymmetry is not
    enforced by any type check; it is a discipline every ``raise
    ServingLimitError(...)`` call must keep on its own.
    """


def new_correlation_id() -> str:
    """Return one unpredictable id for a single request or refusal.

    Sixteen lowercase hex characters (64 bits) from :func:`secrets.token_hex`
    -- a user can quote it in a support request and an operator can grep it
    out of the service log, closing the loop a 2026-09-06 audit found open:
    two refusals that week were diagnosed only by reading code and
    reproducing the request against three servers, because nothing tied the
    response a user saw to a line in any log. Drawn from the OS CSPRNG, not
    from the artifact, the corpus, or the request itself, so it never carries
    information about any of them and two callers can never coin the same id
    on purpose; the 64 bits of randomness make an accidental collision
    negligible at any volume this project serves.
    """

    return secrets.token_hex(8)


#: The CLI's half of one dialect for refusing (2026-09-07 audit, items 9,
#: 12, 13): the same three classes ``api/router.py``'s ``_REFUSAL_HINTS``
#: answers for HTTP, so a person who hits the same underlying condition
#: through either surface reads the same "what to do instead." Public, and
#: imported by ``spicysearch.validation.__main__`` and
#: ``spicysearch.experiments.__main__`` -- the import direction (both may
#: import Search) makes sharing this cheaper than each dispatcher
#: reimplementing it and drifting the moment one of the three changes
#: (2026-09-07 follow-up: found drifted on the first review).
#:
#: It lives here rather than in ``cli.py`` because the validation and
#: experiments dispatchers need exactly this dict and one writer, and
#: importing them from the search CLI pulled that whole module graph in with
#: them. The size of that reduction is deliberately not quoted here: three
#: separate measurements of it disagreed (121/538, 538/128, 92/526) because
#: the count depends on what a probing interpreter has already loaded, and
#: this repository does not quote a number without a receipt beside the
#: command that produced it. The direction is robust and is the whole point.
#: ``canonical`` already holds
#: every error type these three classify and is already imported by all of
#: them.
#:
#: **The HTTP wording differs on purpose and this is the note that keeps that
#: a decision.** ``api/router.py`` tells a reader to report the requestId to
#: an operator; here it does not, because a CLI process has no separate access
#: log and its own stderr *is* the log.
#:
#: **That is not the only divergence and an earlier version of this note said
#: it was.** ``invalid_request`` is the one code both tables key, and its first
#: sentences differ too -- "Fix the command's arguments" against "Fix the
#: request named in this refusal's message" -- because a CLI has arguments and
#: an HTTP caller has a request. Also surface-appropriate, also deliberate, and
#: it was not covered by a note claiming a single exception.
#:
#: **One condition is not covered by "one dialect" and the claim should not be
#: read as covering it** (2026-09-07 round two, found by execution). A snapshot
#: that simply does not carry an optional lane classifies as
#: ``invalid_request`` on the CLI and ``not_found`` over HTTP, and **both hints
#: are advice that cannot work**: the arguments are fine and no route is
#: missing -- the deployment lacks a capability the request asked for. Neither
#: surface has a code for that, so each reaches for its nearest wrong one and
#: they reach differently.
#:
#: Not fixed here on purpose. The honest fix is a class these tables do not
#: have -- "this deployment cannot answer that, and it is nobody's mistake" --
#: and inventing a fourth refusal class is a product decision rather than a
#: review follow-up. Recorded so the next reader knows the alignment is three
#: classes wide, not four, and does not verify the claim against this case and
#: conclude the tables are wrong.

#: The fallback for a code with no entry of its own. A default, never a
#: promise that the advice fits -- same rule the HTTP table states for its own.
_UNCLASSIFIED_CLI_HINT = (
    "This refusal has no specific guidance registered. Keep this output -- "
    "the requestId identifies it."
)

CLI_REFUSAL_HINTS: dict[str, str] = {
    "invalid_request": "Fix the command's arguments and try again.",
    "serving_limit": (
        "The request is valid but too large or expensive to serve right "
        "now. Narrow it -- fewer words, an added filter, or a shorter "
        "phrase or quoted span -- and try again."
    ),
    "integrity_refusal": (
        "This means the verified state disagrees with its own seal, not "
        "that the command was wrong. Retrying will not help; keep this "
        "output -- the requestId identifies this refusal in it."
    ),
}


def write_cli_refusal(code: str, error: BaseException) -> None:
    """Write one refusal to stderr as JSON, with a hint and a correlation id.

    A CLI process has no separate access log to correlate against, so the
    process's own stderr -- where this already writes the cause as
    ``message`` -- is the log ``requestId`` needs to appear beside; there is
    no second logging call to make. See ``error_response`` in
    ``api/router.py`` for the HTTP twin of this same shape.
    """

    sys.stderr.buffer.write(
        canonical_json_bytes(
            {
                "error": {
                    "code": code,
                    "message": str(error),
                    # ``.get`` with a fallback, matching the HTTP twin's
                    # ``_REFUSAL_HINTS.get``. A bare subscript made a fourth,
                    # unregistered code raise a KeyError *inside the refusal
                    # writer* -- a traceback in the one place whose job is to
                    # turn a failure into a message.
                    "hint": CLI_REFUSAL_HINTS.get(code, _UNCLASSIFIED_CLI_HINT),
                    "requestId": new_correlation_id(),
                }
            }
        )
        + b"\n"
    )


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic UTF-8 JSON bytes for SpicySearch product data."""

    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_digest(value: bytes | Any) -> str:
    """Return a lowercase, algorithm-qualified SHA-256 digest."""

    raw = value if isinstance(value, bytes) else canonical_json_bytes(value)
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


def canonical_json_array_sha256(values: Iterable[Any]) -> tuple[str, int]:
    """Stream the bare SHA-256 of one canonical JSON array and its item count."""

    digest = hashlib.sha256(b"[")
    count = 0
    for value in values:
        if count:
            digest.update(b",")
        digest.update(canonical_json_bytes(value))
        count += 1
    digest.update(b"]")
    return digest.hexdigest(), count


class MultiSectionFramedHasher:
    """Stream ``docspec``'s framed-digest byte protocol across many sections
    under one running hash, so a whole-state digest can share a traversal with
    each section's own digest instead of re-reading and re-validating every
    record a second time.

    ``docspec.adapters.framing.FramedSectionHasher`` restates
    ``framed_section_digest`` incrementally for exactly one section (domain,
    NUL, name length, name, count, then per record a length-prefixed payload).
    A combined digest such as ``outputStateDigest`` or ``compositionStateDigest``
    seals several named sections, in order, under one domain header instead —
    the same byte protocol, just with more than one name/count/records block
    before the final digest. Rulespec has no incremental primitive for that
    shape, so this restates it directly: one ``hashlib.sha256`` object that
    keeps accumulating across ``start_section``/``add_payload`` calls, instead
    of sealing after one section. Byte-for-byte equality with calling
    ``framed_section_digest_fast(domain, sections)`` once, with every section
    fully materialized, is pinned by
    ``test_multi_section_framed_hasher_matches_batch_digest``.

    A caller that also needs one section's own standalone digest computes it
    with a sibling ``FramedSectionHasher`` fed the same canonicalized payload
    bytes in lockstep, so every record is validated and canonicalized exactly
    once no matter how many digests it feeds.
    """

    __slots__ = ("_count", "_digest", "_domain", "_name", "_names", "_observed")

    def __init__(self, domain: str) -> None:
        if not isinstance(domain, str) or not domain:
            raise IntegrityError("digest domain must be nonempty text")
        self._digest = hashlib.sha256(domain.encode("utf-8") + b"\0")
        self._domain = domain
        self._names: set[str] = set()
        self._name: str | None = None
        self._count = 0
        self._observed = 0

    def start_section(self, name: str, count: int) -> None:
        """Close the current section, if any, and open the next one."""

        self._close_current()
        if not name or name in self._names:
            raise IntegrityError("section names must be nonempty and distinct")
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise IntegrityError(
                f"cannot compute {self._domain}: section count must be a non-negative integer"
            )
        self._names.add(name)
        name_bytes = name.encode("utf-8")
        self._digest.update(struct.pack(">Q", len(name_bytes)))
        self._digest.update(name_bytes)
        self._digest.update(struct.pack(">Q", count))
        self._name = name
        self._count = count
        self._observed = 0

    def add_payload(self, payload: bytes) -> None:
        """Feed one record's already-canonicalized payload bytes."""

        if self._name is None:
            raise IntegrityError(f"cannot compute {self._domain}: no section is open")
        self._observed += 1
        if self._observed > self._count:
            raise IntegrityError(
                f"cannot compute {self._domain}: section {self._name!r} exceeds its declared count"
            )
        self._digest.update(struct.pack(">Q", len(payload)))
        self._digest.update(payload)

    def _close_current(self) -> None:
        if self._name is not None and self._observed != self._count:
            raise IntegrityError(
                f"cannot compute {self._domain}: section {self._name!r} declared "
                f"{self._count} records but yielded {self._observed}"
            )

    def digest(self) -> str:
        """Close the final section and return the qualified digest."""

        self._close_current()
        return "sha256:" + self._digest.hexdigest()


def stable_id(prefix: str, identity: Any) -> str:
    """Derive a stable URN from identity-defining fields."""

    return f"{prefix}:{sha256_digest(identity).removeprefix('sha256:')}"


def read_json(path: Path) -> dict[str, Any]:
    """Read one JSON object without accepting a scalar or array root."""

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise IntegrityError(f"{path} must contain a JSON object")
    return value


_QUALIFIED_SHA256 = re.compile(r"sha256:[0-9a-f]{64}")


@functools.lru_cache(maxsize=65536)
def _is_qualified_sha256(value: str) -> bool:
    return _QUALIFIED_SHA256.fullmatch(value) is not None


def qualified_sha256(value: object, *, label: str) -> str:
    """Return one algorithm-qualified SHA-256 digest: ``"sha256:"`` plus exactly
    64 lowercase hex characters. Raises :class:`IntegrityError` otherwise.

    The same few digests recur across every unit and identifier of a build,
    so the verdict is cached per string; the check itself is one regex match.
    """

    if not isinstance(value, str) or not _is_qualified_sha256(value):
        raise IntegrityError(f"{label} must be one qualified lowercase SHA-256 digest")
    return value


def logical_id_digest(value: str, *, label: str) -> str:
    """Return the algorithm-qualified SHA-256 digest suffix of a logical ID.

    Splits ``value`` on the final ``":"`` and requires the trailing segment to
    be exactly 64 lowercase hex characters, returning it qualified with the
    ``"sha256:"`` prefix. Raises :class:`IntegrityError` otherwise.
    """

    suffix = value.rsplit(":", 1)[-1]
    if len(suffix) != 64 or any(character not in "0123456789abcdef" for character in suffix):
        raise IntegrityError(f"{label} must end in a lowercase, 64-character SHA-256 digest")
    return "sha256:" + suffix
