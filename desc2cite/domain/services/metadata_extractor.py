from __future__ import annotations

import re
import unicodedata

from desc2cite.domain.models import ExtractedPaper, PaperRecord

_NON_WORD_PATTERN = re.compile(r"[^A-Za-z0-9]+")
_TITLE_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+")
_KEY_STOPWORDS = {"a", "an", "and", "for", "in", "of", "on", "the", "to", "with"}


def extract_paper_metadata(record: PaperRecord) -> ExtractedPaper:
    fields: dict[str, str] = {"title": record.title}

    if record.authors:
        fields["author"] = " and ".join(record.authors)
    if record.year:
        fields["year"] = str(record.year)
    if record.venue:
        venue_field = "journal" if record.entry_type == "article" else "booktitle"
        fields[venue_field] = record.venue
    if record.publisher:
        fields["publisher"] = record.publisher
    if record.volume:
        fields["volume"] = record.volume
    if record.number:
        fields["number"] = record.number
    if record.pages:
        fields["pages"] = record.pages
    if record.doi:
        fields["doi"] = record.doi
    if record.url:
        fields["url"] = record.url

    for key, value in record.extra_fields.items():
        if value:
            fields[key] = str(value)

    return ExtractedPaper(record=record, bibtex_key=build_bibtex_key(record), fields=fields)


def build_bibtex_key(record: PaperRecord) -> str:
    author_part = "unknown"
    if record.authors:
        author_part = _slugify(record.authors[0].split()[-1]) or "unknown"

    year_part = str(record.year) if record.year else "nd"
    title_part = "paper"
    for token in _TITLE_TOKEN_PATTERN.findall(record.title):
        if token.casefold() not in _KEY_STOPWORDS:
            title_part = _slugify(token)
            break

    return f"{author_part}{year_part}{title_part}"


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return _NON_WORD_PATTERN.sub("", ascii_text).lower()
