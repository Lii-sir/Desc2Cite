from __future__ import annotations

from desc2cite.domain.models import PipelineResult
from desc2cite.domain.services import (
    extract_paper_metadata,
    format_citation,
    generate_bibtex,
    optimize_query,
    rerank_results,
)
from desc2cite.infrastructure.ai.query_rewriter import QueryRewriter
from desc2cite.infrastructure.search.academic_search_engine import AcademicSearchEngine


class DescToCiteService:
    """Application service that orchestrates the full description-to-citation flow."""

    def __init__(self, search_engine: AcademicSearchEngine, query_rewriter: QueryRewriter | None = None) -> None:
        self.search_engine = search_engine
        self.query_rewriter = query_rewriter

    def run(self, description: str, top_k: int = 5, style: str = "apa") -> PipelineResult:
        rewritten_text = self.query_rewriter.rewrite(description) if self.query_rewriter else None
        original_query = optimize_query(description)
        query = optimize_query(rewritten_text or description)
        query.original_text = description
        query.rewritten_text = rewritten_text
        query.tokens = _merge_unique(query.tokens, original_query.tokens)
        query.candidate_phrases = _merge_unique(query.candidate_phrases, original_query.candidate_phrases)
        query.candidate_queries = _merge_unique(
            [item for item in [rewritten_text] if item],
            query.candidate_queries,
            original_query.candidate_queries,
        )
        if query.year_hint is None:
            query.year_hint = original_query.year_hint

        initial_results = self.search_engine.search(query, limit=max(top_k, 1))
        ranked_results = rerank_results(query, initial_results)
        chosen = ranked_results[0] if ranked_results else None

        if chosen is None:
            return PipelineResult(
                query=query,
                matches=[],
                chosen=None,
                bibtex=None,
                formatted_citation=None,
            )

        extracted = extract_paper_metadata(chosen.record)
        return PipelineResult(
            query=query,
            matches=ranked_results,
            chosen=chosen,
            bibtex=generate_bibtex(extracted),
            formatted_citation=format_citation(chosen.record, style=style),
        )


def _merge_unique(*collections: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for collection in collections:
        for item in collection:
            key = item.casefold()
            if key in seen:
                continue
            merged.append(item)
            seen.add(key)
    return merged
