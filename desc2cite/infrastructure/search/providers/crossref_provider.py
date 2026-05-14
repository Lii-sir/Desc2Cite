from __future__ import annotations

import json
import urllib.parse
import urllib.request

from desc2cite.domain.models import PaperRecord, SearchQuery, SearchResult
from desc2cite.infrastructure.search.providers.base import SearchProvider
from desc2cite.infrastructure.search.scoring import overlap_score


class CrossrefSearchProvider(SearchProvider):
    source_name = "crossref"

    def __init__(self, mailto: str | None = None, timeout: float = 8.0) -> None:
        self.mailto = mailto
        self.timeout = timeout

    def search(self, query: SearchQuery, limit: int = 10) -> list[SearchResult]:
        all_results: dict[str, SearchResult] = {}
        for candidate in query.candidate_queries[:3] or [query.original_text]:
            for result in self._search_candidate(candidate, query, limit=limit):
                key = (result.record.doi or result.record.title).casefold()
                existing = all_results.get(key)
                if existing is None or result.score > existing.score:
                    all_results[key] = result

        return sorted(all_results.values(), key=lambda item: item.score, reverse=True)[:limit]

    def _search_candidate(self, candidate: str, query: SearchQuery, limit: int) -> list[SearchResult]:
        params = {
            "query.bibliographic": candidate,
            "rows": str(max(limit, 1)),
            "select": ",".join(
                [
                    "title",
                    "author",
                    "DOI",
                    "URL",
                    "container-title",
                    "published-print",
                    "published-online",
                    "issued",
                    "publisher",
                    "volume",
                    "issue",
                    "page",
                    "type",
                ]
            ),
        }
        if self.mailto:
            params["mailto"] = self.mailto

        url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, headers={"User-Agent": "Desc2Cite/0.1"})

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return []

        query_tokens = set(query.tokens)
        results: list[SearchResult] = []
        for item in payload.get("message", {}).get("items", []):
            title = " ".join(item.get("title") or []).strip()
            if not title:
                continue

            authors = []
            for author in item.get("author") or []:
                given = author.get("given", "").strip()
                family = author.get("family", "").strip()
                full_name = " ".join(part for part in [given, family] if part)
                if full_name:
                    authors.append(full_name)

            record = PaperRecord(
                title=title,
                authors=authors,
                year=_extract_crossref_year(item),
                venue=" ".join(item.get("container-title") or []).strip() or None,
                doi=item.get("DOI"),
                url=item.get("URL"),
                entry_type=_map_crossref_type(item.get("type")),
                publisher=item.get("publisher"),
                volume=item.get("volume"),
                number=item.get("issue"),
                pages=item.get("page"),
            )
            score = (overlap_score(query_tokens, record.title) * 0.8) + (overlap_score(query_tokens, record.venue or "") * 0.2)
            results.append(SearchResult(record=record, score=score, source=self.source_name, reasons=["remote lookup"]))

        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]


def _extract_crossref_year(item: dict) -> int | None:
    date_parts = (
        item.get("published-print", {}).get("date-parts")
        or item.get("published-online", {}).get("date-parts")
        or item.get("issued", {}).get("date-parts")
        or []
    )
    try:
        return int(date_parts[0][0])
    except (IndexError, TypeError, ValueError):
        return None


def _map_crossref_type(crossref_type: str | None) -> str:
    mapping = {
        "journal-article": "article",
        "proceedings-article": "inproceedings",
        "book-chapter": "incollection",
        "book": "book",
    }
    return mapping.get(crossref_type or "", "article")
