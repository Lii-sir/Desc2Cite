from __future__ import annotations

import re

from desc2cite.domain.models import SearchQuery, SearchResult
from desc2cite.infrastructure.search.scoring import acronym_match_bonus

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*|[\u4e00-\u9fff]+")


def _tokenize(text: str) -> set[str]:
    return {token.casefold() for token in _TOKEN_PATTERN.findall(text or "")}


def rerank_results(query: SearchQuery, results: list[SearchResult]) -> list[SearchResult]:
    query_tokens = set(query.tokens)

    for result in results:
        title_tokens = _tokenize(result.record.title)
        matched_tokens = len(query_tokens & title_tokens)
        coverage_bonus = (matched_tokens / max(len(query_tokens), 1)) * 0.15
        result.score += coverage_bonus
        acronym_bonus = acronym_match_bonus(query_tokens, result.record.title)
        if acronym_bonus:
            result.score += acronym_bonus
            result.reasons.append("acronym/title match")

        if result.record.doi:
            result.score += 0.04
            result.reasons.append("has DOI")

        if result.record.authors and result.record.year and result.record.venue:
            result.score += 0.05
            result.reasons.append("complete citation metadata")

        if query.year_hint and result.record.year == query.year_hint:
            result.score += 0.05

    return sorted(results, key=lambda item: item.score, reverse=True)
