from __future__ import annotations

import re

from desc2cite.domain.models import SearchQuery

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "paper",
    "papers",
    "research",
    "show",
    "study",
    "that",
    "the",
    "this",
    "to",
    "want",
    "with",
    "\u6211",
    "\u60f3",
    "\u5b9e\u73b0",
    "\u5173\u4e8e",
    "\u8bba\u6587",
    "\u6587\u732e",
    "\u5f15\u7528",
    "\u4e00\u7bc7",
    "\u76f8\u5173",
    "\u627e\u5230",
    "\u7ecf\u5178",
    "\u7ecf\u5178\u8bba\u6587",
    "\u90a3\u7bc7",
    "\u8457\u540d",
    "\u8457\u540d\u8bba\u6587",
}

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*|[\u4e00-\u9fff]+")
_YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")
_QUOTED_PATTERN = re.compile(r"['\"\u201c\u201d\u2018\u2019](.+?)['\"\u201c\u201d\u2018\u2019]")


def _normalize(text: str) -> str:
    lowered = text.casefold()
    return re.sub(r"\s+", " ", lowered).strip()


def _tokenize(text: str) -> list[str]:
    return [token for token in _TOKEN_PATTERN.findall(text.casefold())]


def optimize_query(text: str) -> SearchQuery:
    normalized = _normalize(text)
    tokens = _tokenize(text)
    informative_tokens = [token for token in tokens if token not in _STOPWORDS and len(token) > 1]
    year_match = _YEAR_PATTERN.search(text)
    phrases = [match.group(1).strip() for match in _QUOTED_PATTERN.finditer(text) if match.group(1).strip()]

    candidate_queries: list[str] = [text.strip()]
    if informative_tokens:
        candidate_queries.append(" ".join(informative_tokens[:12]))
    if phrases:
        candidate_queries.extend(phrases[:3])

    deduped_queries: list[str] = []
    seen: set[str] = set()
    for candidate in candidate_queries:
        key = candidate.casefold()
        if candidate and key not in seen:
            deduped_queries.append(candidate)
            seen.add(key)

    return SearchQuery(
        original_text=text,
        normalized_text=normalized,
        tokens=informative_tokens or tokens,
        rewritten_text=None,
        candidate_phrases=phrases,
        candidate_queries=deduped_queries,
        year_hint=int(year_match.group(1)) if year_match else None,
    )
