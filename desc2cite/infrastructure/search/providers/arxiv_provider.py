from __future__ import annotations

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from desc2cite.domain.models import PaperRecord, SearchQuery, SearchResult
from desc2cite.infrastructure.search.providers.base import SearchProvider
from desc2cite.infrastructure.search.scoring import overlap_score

_ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivSearchProvider(SearchProvider):
    source_name = "arxiv"

    def __init__(self, timeout: float = 12.0) -> None:
        self.timeout = timeout

    def search(self, query: SearchQuery, limit: int = 10) -> list[SearchResult]:
        all_results: dict[str, SearchResult] = {}

        for candidate in query.candidate_queries[:3] or [query.original_text]:
            results = self._search_candidate(candidate, query, limit=limit)
            for result in results:
                key = (result.record.doi or result.record.url or result.record.title).casefold()
                existing = all_results.get(key)
                if existing is None or result.score > existing.score:
                    all_results[key] = result

        return sorted(all_results.values(), key=lambda item: item.score, reverse=True)[:limit]

    def _search_candidate(self, candidate: str, query: SearchQuery, limit: int) -> list[SearchResult]:
        params = {
            "search_query": f"all:{candidate}",
            "start": "0",
            "max_results": str(max(limit, 1)),
        }
        url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, headers={"User-Agent": "Desc2Cite/0.1"})

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = response.read()
        except Exception:
            return []

        try:
            root = ET.fromstring(payload)
        except ET.ParseError:
            return []

        query_tokens = set(query.tokens)
        results: list[SearchResult] = []
        for entry in root.findall("atom:entry", _ATOM_NS):
            title = _get_text(entry, "atom:title")
            if not title:
                continue

            abstract = _get_text(entry, "atom:summary") or None
            authors = [author.text.strip() for author in entry.findall("atom:author/atom:name", _ATOM_NS) if author.text]
            url = _get_text(entry, "atom:id") or None
            doi = _get_text(entry, "arxiv:doi") or None
            year = _extract_year(_get_text(entry, "atom:published"))
            journal_ref = _get_text(entry, "arxiv:journal_ref") or None

            record = PaperRecord(
                title=title,
                authors=authors,
                year=year,
                venue=journal_ref,
                abstract=abstract,
                doi=doi,
                url=url,
                entry_type="article" if doi or journal_ref else "misc",
            )

            title_score = overlap_score(query_tokens, record.title)
            abstract_score = overlap_score(query_tokens, record.abstract or "")
            score = (title_score * 0.75) + (abstract_score * 0.25)
            reasons = []
            if title_score:
                reasons.append(f"title overlap {title_score:.2f}")
            if abstract_score:
                reasons.append(f"abstract overlap {abstract_score:.2f}")
            if doi:
                score += 0.05
                reasons.append("has DOI")
            if query.year_hint and record.year == query.year_hint:
                score += 0.05
                reasons.append(f"matched year {query.year_hint}")

            if score <= 0:
                continue

            results.append(
                SearchResult(
                    record=record,
                    score=score,
                    source=self.source_name,
                    reasons=reasons or ["remote lookup"],
                )
            )

        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]


def _get_text(entry: ET.Element, path: str) -> str:
    node = entry.find(path, _ATOM_NS)
    return node.text.strip() if node is not None and node.text else ""


def _extract_year(published_text: str) -> int | None:
    if not published_text or len(published_text) < 4:
        return None
    try:
        return int(published_text[:4])
    except ValueError:
        return None
