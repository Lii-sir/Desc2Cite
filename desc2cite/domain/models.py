from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SearchQuery:
    original_text: str
    normalized_text: str
    tokens: list[str]
    rewritten_text: str | None = None
    candidate_phrases: list[str] = field(default_factory=list)
    candidate_queries: list[str] = field(default_factory=list)
    year_hint: int | None = None


@dataclass(slots=True)
class PaperRecord:
    title: str
    authors: list[str]
    year: int | None = None
    venue: str | None = None
    abstract: str | None = None
    doi: str | None = None
    url: str | None = None
    entry_type: str = "article"
    publisher: str | None = None
    volume: str | None = None
    number: str | None = None
    pages: str | None = None
    extra_fields: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SearchResult:
    record: PaperRecord
    score: float
    source: str
    reasons: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ExtractedPaper:
    record: PaperRecord
    bibtex_key: str
    fields: dict[str, str]


@dataclass(slots=True)
class PipelineResult:
    query: SearchQuery
    matches: list[SearchResult]
    chosen: SearchResult | None
    bibtex: str | None
    formatted_citation: str | None
