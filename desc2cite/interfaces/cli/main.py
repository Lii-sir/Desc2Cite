from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from desc2cite.bootstrap import build_desc_to_cite_service
from desc2cite.infrastructure.ai import QueryRewriteAuthError, QueryRewriteRequestError, QueryRewriteTimeoutError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Convert natural-language paper descriptions into citations.")
    parser.add_argument("description", nargs="+", help="Natural-language description of the target paper.")
    parser.add_argument("--style", default="apa", choices=["apa", "mla", "plain"], help="Output citation style.")
    parser.add_argument("--top-k", type=int, default=5, help="Number of search candidates to keep.")
    parser.add_argument("--corpus", help="Path to a JSON corpus file.")
    parser.add_argument("--remote", action="store_true", help="Enable Crossref remote search.")
    parser.add_argument("--mailto", help="Optional email for Crossref polite pool usage.")
    parser.add_argument("--ai-rewrite", action="store_true", help="Use AI to rewrite the description into a search query.")
    parser.add_argument("--ai-provider", choices=["minimax", "openai"], help="Preset provider defaults for AI query rewriting.")
    parser.add_argument("--ai-base-url", help="OpenAI-compatible API base URL, for example https://api.openai.com/v1.")
    parser.add_argument("--ai-model", help="Model name used for AI query rewriting.")
    parser.add_argument("--save-bib", help="Write the generated BibTeX to a .bib file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    service = build_desc_to_cite_service(
        corpus_path=args.corpus,
        enable_remote=args.remote,
        crossref_mailto=args.mailto,
        enable_ai_rewrite=args.ai_rewrite,
        ai_provider=args.ai_provider,
        ai_base_url=args.ai_base_url,
        ai_model=args.ai_model,
    )
    description = " ".join(args.description)
    try:
        result = service.run(description=description, top_k=args.top_k, style=args.style)
    except QueryRewriteAuthError as error:
        print(str(error), file=sys.stderr)
        return 2
    except QueryRewriteTimeoutError as error:
        print(str(error), file=sys.stderr)
        return 2
    except QueryRewriteRequestError as error:
        print(str(error), file=sys.stderr)
        return 2

    if args.save_bib and result.bibtex:
        output_path = Path(args.save_bib)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result.bibtex + "\n", encoding="utf-8")

    if args.json:
        payload = {
            "query": {
                "original": result.query.original_text,
                "tokens": result.query.tokens,
                "candidate_queries": result.query.candidate_queries,
                "rewritten_text": result.query.rewritten_text,
                "year_hint": result.query.year_hint,
            },
            "chosen": None
            if result.chosen is None
            else {
                "title": result.chosen.record.title,
                "authors": result.chosen.record.authors,
                "year": result.chosen.record.year,
                "venue": result.chosen.record.venue,
                "doi": result.chosen.record.doi,
                "source": result.chosen.source,
                "score": round(result.chosen.score, 4),
            },
            "citation": result.formatted_citation,
            "bibtex": result.bibtex,
            "matches": [
                {
                    "title": match.record.title,
                    "score": round(match.score, 4),
                    "source": match.source,
                    "reasons": match.reasons,
                }
                for match in result.matches
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if result.chosen is None:
        print("No matching papers found.")
        return 1

    print("Chosen paper:")
    print(f"  {result.chosen.record.title}")
    print()
    print(f"{args.style.upper()} citation:")
    print(result.formatted_citation)
    print()
    print("BibTeX:")
    print(result.bibtex)
    print()
    print("Top matches:")
    for index, match in enumerate(result.matches, start=1):
        print(f"  {index}. {match.record.title} [{match.score:.3f}] ({match.source})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
