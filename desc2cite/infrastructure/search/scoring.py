from __future__ import annotations

import math
import re

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*|[\u4e00-\u9fff]+")
_ACRONYM_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9-]{1,}$")


def tokenize_text(text: str) -> set[str]:
    return {token.casefold() for token in _TOKEN_PATTERN.findall(text or "")}


def overlap_score(query_tokens: set[str], field_text: str) -> float:
    if not query_tokens:
        return 0.0
    field_tokens = tokenize_text(field_text)
    if not field_tokens:
        return 0.0
    intersection = len(query_tokens & field_tokens)
    return intersection / math.sqrt(len(query_tokens) * len(field_tokens))


def acronym_match_bonus(query_tokens: set[str], field_text: str) -> float:
    text_tokens = tokenize_text(field_text)
    bonus = 0.0
    for token in query_tokens:
        if _is_acronym_like(token) and token in text_tokens:
            bonus += 0.35
    return bonus


def _is_acronym_like(token: str) -> bool:
    raw = token.strip()
    if len(raw) < 3:
        return False
    return bool(_ACRONYM_PATTERN.match(raw.upper()))
