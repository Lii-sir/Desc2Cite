from __future__ import annotations

from desc2cite.domain.models import SearchQuery, SearchResult
from desc2cite.infrastructure.search.providers.base import SearchProvider


class AcademicSearchEngine:
    def __init__(self, providers: list[SearchProvider]) -> None:
        self.providers = providers

    def search(self, query: SearchQuery, limit: int = 10) -> list[SearchResult]:
        all_results: list[SearchResult] = []
        for provider in self.providers:
            all_results.extend(provider.search(query, limit=limit))

        deduped: dict[str, SearchResult] = {}
        for result in all_results:
            key = (result.record.doi or result.record.title).casefold()
            existing = deduped.get(key)
            if existing is None or result.score > existing.score:
                deduped[key] = result

        return sorted(deduped.values(), key=lambda item: item.score, reverse=True)[:limit]
