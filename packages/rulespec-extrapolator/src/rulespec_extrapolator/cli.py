"""Command-line entry point for local source understanding and review."""
import argparse
import json
from pathlib import Path

from .core import canonical, validate_graph
from .documents import load_document
from . import extraction as e
from . import audit as a


def _load(path):
    return json.loads(Path(path).read_text())


def _write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Extract and review source-backed rules locally.")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare", help="Pin exact text and section coordinates.")
    prepare.add_argument("source", type=Path, help="Text, prepared document JSON, or USLM XML.")
    prepare.add_argument("--title")
    prepare.add_argument("--source-url", default="")
    prepare.add_argument("--output", type=Path, required=True)
    extract = sub.add_parser("extract", help="Extract candidates; preserve every attempt.")
    extract.add_argument("source", type=Path, help="Text, prepared document JSON, or USLM XML.")
    extract.add_argument("--model", default="gemini-3.8-flash")
    extract.add_argument("--env-file", type=Path)
    extract.add_argument("--max-chars", type=int, default=e.DEFAULT_MAX_CHARS)
    extract.add_argument("--max-output-tokens", type=lambda value: None if value == "provider" else int(value),
                         default=e.MAX_OUTPUT_TOKENS, metavar="TOKENS|provider",
                         help="Total generation allowance; 'provider' omits the application cap. Recorded for replay.")
    extract.add_argument("--thinking-level", choices=("low", "medium", "high"),
                         default=e.DEFAULT_THINKING_LEVEL,
                         help="Gemini thinking effort; default %(default)s. No thinking budget is sent.")
    extract.add_argument("--temperature", type=float, default=0,
                         help="Gemini sampling temperature (0–2), recorded for replay; default 0.")
    extract.add_argument("--output", type=Path, required=True)
    replay = sub.add_parser("replay", help="Reparse saved responses and verify the original graph.")
    replay.add_argument("input", type=Path)
    replay.add_argument("--output", type=Path, required=True)
    reprocess = sub.add_parser("reprocess", help="Process saved responses with this code; preserve the original run.")
    reprocess.add_argument("input", type=Path)
    reprocess.add_argument("--output", type=Path, required=True)
    serve = sub.add_parser("serve", help="Open a local persistent review workspace.")
    serve.add_argument("run", type=Path)
    serve.add_argument("--port", type=int, default=8765)
    serve.add_argument("--audit", type=Path, help="Show a saved source check and mark it stale after corrections.")
    review = sub.add_parser("review", help="Append an explicit review action from JSON.")
    review.add_argument("run", type=Path)
    review.add_argument("--action", type=Path, required=True)
    feedback = sub.add_parser('reference-feedback', help='Record feedback on a saved reference reading without changing claims.')
    feedback.add_argument('run', type=Path)
    feedback.add_argument('--scan', type=Path, required=True, help='Saved references command output.')
    selection = feedback.add_mutually_exclusive_group(required=True)
    selection.add_argument('--candidate', type=int, help='Zero-based index in the scan candidates list.')
    selection.add_argument('--rejected', type=int, help='Zero-based index in the scan rejected list.')
    feedback.add_argument('--expected-revision', type=int, required=True)
    feedback.add_argument('--actor', required=True)
    feedback.add_argument('--actor-kind', choices=('humanUser', 'aiAgent'), default='humanUser')
    feedback.add_argument('--rationale', required=True, help='What appears wrong, missing or disputed in this reading.')
    export = sub.add_parser("export", help="Export and validate the current review state.")
    export.add_argument("run", type=Path)
    export.add_argument("--output", type=Path, required=True)
    discovery = sub.add_parser("discovery-export", help="Export source passages with grounded scope/context links and processing status.")
    discovery.add_argument("run", type=Path)
    discovery.add_argument("--output", type=Path, required=True)
    discovery.add_argument("--references", action="store_true",
                           help="Add source reference candidates using the optional RefSpec and SpicySearch readers.")
    references = sub.add_parser("references", help="Locate supported reference mentions without model calls.")
    references.add_argument("source", type=Path, help="Text, USLM/eCFR XML, prepared document, rulebook JSON, or extraction directory.")
    references.add_argument("--output", type=Path, required=True)
    for command in (references, discovery):
        command.add_argument("--reference-source", type=Path, action="append", default=[],
                             help="Look up exact targets in supplied USLM/eCFR XML or a prepared document; repeat for additional sources or editions.")
        command.add_argument("--act-index", type=Path, help="Use a pinned RefSpec act-index directory for named-act references.")
        command.add_argument("--source-credit-index", type=Path, help="Also consult pinned RefSpec source credits; requires --act-index.")
    evaluate = sub.add_parser("evaluate", help="Score content-bound independent source judgments.")
    evaluate.add_argument("rulebook", type=Path)
    evaluate.add_argument("--labels", type=Path, required=True)
    evaluate.add_argument("--judgments", type=Path)
    evaluate.add_argument("--output", type=Path, required=True)
    audit = sub.add_parser("audit", help="Check the source for omissions, then challenge the draft meaning.")
    audit.add_argument("rulebook", type=Path)
    audit.add_argument("--model", default="gemini-3.8-flash")
    audit.add_argument("--env-file", type=Path)
    audit.add_argument("--max-chars", type=int, default=3000)
    audit.add_argument("--max-output-tokens", type=lambda value: None if value == "provider" else int(value),
                       default=32768, metavar="TOKENS|provider",
                       help="Total generation allowance per audit request; 'provider' omits the application cap.")
    audit.add_argument("--thinking-level", choices=("low", "medium", "high"),
                       default=a.DEFAULT_THINKING_LEVEL,
                       help="Thinking effort for both audit stages; default %(default)s. No thinking budget is sent.")
    audit.add_argument("--output", type=Path, required=True)
    audit_replay = sub.add_parser("audit-replay", help="Recompute a saved audit without provider calls.")
    audit_replay.add_argument("input", type=Path)
    audit_replay.add_argument("--output", type=Path, required=True)
    refine = sub.add_parser("refine", help="Recover missing meaning and link qualifications through recorded AI corrections.")
    refine.add_argument("run", type=Path, help="Review workspace whose history receives the corrections.")
    refine.add_argument("--audit", type=Path, help="Optional audit of the exact current review snapshot.")
    refine.add_argument("--model", default="gemini-3.8-flash")
    refine.add_argument("--env-file", type=Path)
    refine.add_argument("--max-chars", type=int, default=3000)
    refine.add_argument("--output", type=Path, required=True)
    refine_replay = sub.add_parser("refine-replay", help="Verify captured refinement and review history without provider calls.")
    refine_replay.add_argument("input", type=Path)
    refine_replay.add_argument("--output", type=Path, required=True)
    enrich = sub.add_parser("enrich", help="Add actors and defined terms while preserving existing claim fields.")
    enrich.add_argument("run", type=Path)
    enrich.add_argument("--model", default=e.DEFAULT_MODEL)
    enrich.add_argument("--env-file", type=Path)
    enrich.add_argument("--max-chars", type=int, default=e.DEFAULT_MAX_CHARS)
    enrich.add_argument("--output", type=Path, required=True)
    enrich_replay = sub.add_parser("enrich-replay", help="Verify structural enrichment without provider calls.")
    enrich_replay.add_argument("input", type=Path)
    enrich_replay.add_argument("--output", type=Path, required=True)
    vocab = sub.add_parser("vocabulary", help="Suggest RefSpec labels without dropping unmatched text.")
    vocab.add_argument("rulebook", type=Path)
    vocab.add_argument("--snapshot", type=Path)
    vocab.add_argument("--output", type=Path, required=True)
    usage = sub.add_parser('usage', help='Read provider token usage separately from local JSON storage size.')
    usage.add_argument('run', type=Path)
    args = parser.parse_args(argv)
    if args.command == 'usage':
        if not args.run.is_dir():
            parser.error('Usage requires an existing capture directory')
        result = e.recorded_usage(args.run)
        result['local_json_bytes'] = sum(p.stat().st_size for p in args.run.rglob('*.json') if p.is_file())
        result['limitation'] = 'Tokens are provider-reported usage of retained requests, not a billing invoice. Missing usage is unknown. Local JSON copies do not create output tokens; replay makes no provider calls.'
        print(json.dumps(result, indent=2))
        return
    if args.command == "prepare":
        _write_new(args.output, load_document(args.source, title=args.title, source_url=args.source_url))
    elif args.command in ("extract", "replay", "reprocess"):
        from .extraction import extract_run, replay_run, reprocess_run
        if args.command == "extract":
            result = extract_run(load_document(args.source), args.output, args.model,
                                 env_file=args.env_file, max_chars=args.max_chars, temperature=args.temperature,
                                 max_output_tokens=args.max_output_tokens, thinking_level=args.thinking_level)
        elif args.command == "replay":
            result = replay_run(args.input, args.output)
        else:
            result = reprocess_run(args.input, args.output)
        print(json.dumps({"output": str(args.output), "accepted": len(result["accepted"]),
                          "rejected": len(result["rejected"]), "unresolved": len(result["unresolved"]),
                          "status": result["run"].get("status")}, indent=2))
    elif args.command == "serve":
        from .review import serve
        serve(args.run, port=args.port, audit_dir=args.audit)
    elif args.command in ("review", "export"):
        from .review_store import ReviewStore
        store = ReviewStore(args.run)
        if args.command == "review":
            result = store.apply(_load(args.action))
            print(canonical(result))
        else:
            result = store.snapshot()
            result["validation"] = validate_graph(result["graph"])
            _write_new(args.output, result)
    elif args.command == 'reference-feedback':
        from .reference_feedback import reference_observation
        from .review_store import ReviewStore
        store = ReviewStore(args.run)
        collection, index = ('candidates', args.candidate) if args.candidate is not None else ('rejected', args.rejected)
        observation = reference_observation(store.document, _load(args.scan), collection, index, message=args.rationale)
        result = store.apply({'expected_revision': args.expected_revision, 'actor': args.actor,
                              'actor_kind': args.actor_kind, 'action': 'observe', 'targets': [],
                              'rationale': args.rationale, 'observations': [observation]})
        print(canonical({'revision': result['revision'], 'event': result['history'][-1]}))
    elif args.command == "discovery-export":
        from .discovery import export_discovery
        from .review_store import ReviewStore
        _write_new(args.output, export_discovery(ReviewStore(args.run).snapshot(), include_references=args.references,
                                               act_index=args.act_index, source_credit_index=args.source_credit_index,
                                               reference_sources=[load_document(p) for p in args.reference_source]))
    elif args.command == "references":
        from .references import scan_references
        source = args.source / 'document.json' if args.source.is_dir() else args.source
        if source.suffix == '.json':
            value = _load(source)
            document = value.get('document', value)
        else:
            document = load_document(source)
        _write_new(args.output, scan_references(document, act_index=args.act_index, source_credit_index=args.source_credit_index,
                                               reference_sources=[load_document(p) for p in args.reference_source]))
    elif args.command == "evaluate":
        from .evaluation import evaluate
        result = evaluate(_load(args.rulebook), _load(args.labels),
                          _load(args.judgments) if args.judgments else None)
        _write_new(args.output, result)
    elif args.command == "vocabulary":
        from .vocabulary import annotate, load_vocabulary
        result = annotate(_load(args.rulebook), load_vocabulary(args.snapshot) if args.snapshot else None)
        _write_new(args.output, result)
    elif args.command in ("enrich", "enrich-replay"):
        from .structure import enrich_run, replay_enrichment
        result = (enrich_run(args.run, args.output, args.model, env_file=args.env_file, max_chars=args.max_chars)
                  if args.command == "enrich" else replay_enrichment(args.input, args.output))
        print(json.dumps({k: result[k] for k in ("status", "applied_actions")}))
    elif args.command in ("refine", "refine-replay"):
        from .refinement import refine_run, replay_refinement
        if args.command == "refine":
            result = refine_run(args.run, args.output, args.model, audit_dir=args.audit,
                                env_file=args.env_file, max_chars=args.max_chars)
            print(json.dumps({"output": str(args.output), "status": result["run"]["status"],
                              "applied_actions": result["run"]["applied_actions"], "usage": result["run"]["usage"]}))
        else:
            print(json.dumps(replay_refinement(args.input, args.output)))
    elif args.command in ("audit", "audit-replay"):
        from .audit import audit_run, replay_audit
        result = (audit_run(_load(args.rulebook), args.output, args.model, env_file=args.env_file, max_chars=args.max_chars,
                            max_output_tokens=args.max_output_tokens, thinking_level=args.thinking_level)
                  if args.command == "audit" else replay_audit(args.input, args.output))
        print(json.dumps({"output": str(args.output), "status": result["status"],
                          "review_complete": result["review_complete"], "semantic_completeness": result["semantic_completeness"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
