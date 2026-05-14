from __future__ import annotations

import json
import urllib.parse
import urllib.request

from desc2cite.domain.models import PaperRecord, SearchQuery, SearchResult
from desc2cite.infrastructure.search.providers.base import SearchProvider
from desc2cite.infrastructure.search.scoring import acronym_match_bonus, overlap_score


class SemanticScholarSearchProvider(SearchProvider):
    source_name = "semantic_scholar"

    def __init__(self, timeout: float = 12.0) -> None:
        self.timeout = timeout

    def search(self, query: SearchQuery, limit: int = 10) -> list[SearchResult]:
        all_results: dict[str, SearchResult] = {}

        for candidate in query.candidate_queries[:3] or [query.original_text]:
            for result in self._search_candidate(candidate, query, limit=limit):
                key = (result.record.doi or result.record.url or result.record.title).casefold()
                existing = all_results.get(key)
                if existing is None or result.score > existing.score:
                    all_results[key] = result

        return sorted(all_results.values(), key=lambda item: item.score, reverse=True)[:limit]

    def _search_candidate(self, candidate: str, query: SearchQuery, limit: int) -> list[SearchResult]:
        params = {
            "query": candidate,
            "limit": str(max(limit, 1)),
            "fields": ",".join(
                [
                    "title",
                    "authors",
                    "year",
                    "abstract",
                    "venue",
                    "url",
                    "externalIds",
                ]
            ),
        }
        url = "https://api.semanticscholar.org/graph/v1/paper/search?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, headers={"User-Agent": "Desc2Cite/0.1"})

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        query_tokens = set(query.tokens)
        results: list[SearchResult] = []
        for item in payload.get("data", []):
            title = (item.get("title") or "").strip()
            if not title:
                continue

            authors = [author.get("name", "").strip() for author in item.get("authors") or [] if author.get("name")]
            doi = (item.get("externalIds") or {}).get("DOI")
            record = PaperRecord(
                title=title,
                authors=authors,
                year=item.get("year"),
                venue=(item.get("venue") or "").strip() or None,
                abstract=(item.get("abstract") or "").strip() or None,
                doi=doi,
                url=item.get("url"),
                entry_type="article",
            )

            title_score = overlap_score(query_tokens, record.title)
            abstract_score = overlap_score(query_tokens, record.abstract or "")
            score = (title_score * 0.75) + (abstract_score * 0.2)
            score += acronym_match_bonus(query_tokens, record.title)
            reasons = ["remote lookup"]
            if title_score:
                reasons.append(f"title overlap {title_score:.2f}")
            if abstract_score:
                reasons.append(f"abstract overlap {abstract_score:.2f}")
            if query.year_hint and record.year == query.year_hint:
                score += 0.05
                reasons.append(f"matched year {query.year_hint}")
            if doi:
                score += 0.03
                reasons.append("has DOI")

            if score <= 0:
                continue

            results.append(SearchResult(record=record, score=score, source=self.source_name, reasons=reasons))

        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]
