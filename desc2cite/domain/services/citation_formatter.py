from __future__ import annotations

from desc2cite.domain.models import PaperRecord


def format_citation(record: PaperRecord, style: str = "apa") -> str:
    normalized_style = style.casefold()
    if normalized_style == "mla":
        return _format_mla(record)
    if normalized_style == "plain":
        return _format_plain(record)
    return _format_apa(record)


def _format_apa(record: PaperRecord) -> str:
    authors = _format_authors_apa(record.authors)
    year = f"({record.year})." if record.year else "(n.d.)."
    venue = record.venue or ""
    parts = [part for part in [authors, year, f"{record.title}.", venue] if part]
    citation = " ".join(parts).strip()
    if record.doi:
        citation += f" https://doi.org/{record.doi}"
    elif record.url:
        citation += f" {record.url}"
    return citation


def _format_mla(record: PaperRecord) -> str:
    authors = ", ".join(record.authors) if record.authors else "Unknown author"
    year = str(record.year) if record.year else "n.d."
    venue = record.venue or ""
    parts = [f'{authors}. "{record.title}."', venue, year]
    citation = " ".join(part for part in parts if part).strip()
    if record.url:
        citation += f". {record.url}"
    return citation


def _format_plain(record: PaperRecord) -> str:
    authors = ", ".join(record.authors) if record.authors else "Unknown author"
    year = str(record.year) if record.year else "n.d."
    venue = f" {record.venue}." if record.venue else ""
    return f"{authors} ({year}). {record.title}.{venue}"


def _format_authors_apa(authors: list[str]) -> str:
    if not authors:
        return "Unknown author"

    formatted = []
    for author in authors:
        parts = author.split()
        if len(parts) == 1:
            formatted.append(parts[0])
            continue
        surname = parts[-1]
        initials = " ".join(f"{part[0]}." for part in parts[:-1] if part)
        formatted.append(f"{surname}, {initials}".strip())

    if len(formatted) == 1:
        return formatted[0]
    if len(formatted) == 2:
        return " & ".join(formatted)
    return ", ".join(formatted[:-1]) + f", & {formatted[-1]}"
