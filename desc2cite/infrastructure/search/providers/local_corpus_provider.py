from __future__ import annotations

import json
from pathlib import Path

from desc2cite.domain.models import PaperRecord, SearchQuery, SearchResult
from desc2cite.infrastructure.search.providers.base import SearchProvider
from desc2cite.infrastructure.search.scoring import overlap_score


class LocalCorpusSearchProvider(SearchProvider):
    source_name = "local_corpus"

    def __init__(self, corpus_path: str | Path) -> None:
        path = Path(corpus_path)
        with path.open("r", encoding="utf-8") as file:
            raw_records = json.load(file)
        self.records = [PaperRecord(**record) for record in raw_records]

    def search(self, query: SearchQuery, limit: int = 10) -> list[SearchResult]:
        query_tokens = set(query.tokens)
        results: list[SearchResult] = []

        for record in self.records:
            title_score = overlap_score(query_tokens, record.title)
            abstract_score = overlap_score(query_tokens, record.abstract or "")
            author_score = overlap_score(query_tokens, " ".join(record.authors))
            venue_score = overlap_score(query_tokens, record.venue or "")
            score = (title_score * 0.6) + (abstract_score * 0.25) + (author_score * 0.1) + (venue_score * 0.05)
            reasons: list[str] = []

            for phrase in query.candidate_phrases:
                if phrase.casefold() in record.title.casefold():
                    score += 0.2
                    reasons.append(f"title contains phrase '{phrase}'")

            if query.year_hint and record.year == query.year_hint:
                score += 0.08
                reasons.append(f"matched year {query.year_hint}")

            if score <= 0:
                continue

            if title_score:
                reasons.append(f"title overlap {title_score:.2f}")
            if abstract_score:
                reasons.append(f"abstract overlap {abstract_score:.2f}")
            results.append(
                SearchResult(
                    record=record,
                    score=score,
                    source=self.source_name,
                    reasons=reasons,
                )
            )

        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]
