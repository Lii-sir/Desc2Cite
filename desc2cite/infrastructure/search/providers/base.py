from __future__ import annotations

from abc import ABC, abstractmethod

from desc2cite.domain.models import SearchQuery, SearchResult


class SearchProvider(ABC):
    source_name = "provider"

    @abstractmethod
    def search(self, query: SearchQuery, limit: int = 10) -> list[SearchResult]:
        raise NotImplementedError
