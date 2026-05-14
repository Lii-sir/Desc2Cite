from __future__ import annotations

from desc2cite.domain.models import ExtractedPaper


def generate_bibtex(extracted: ExtractedPaper) -> str:
    entry_type = extracted.record.entry_type or "article"
    lines = [f"@{entry_type}{{{extracted.bibtex_key},"]
    for field, value in extracted.fields.items():
        escaped = value.replace("{", "\\{").replace("}", "\\}")
        lines.append(f"  {field} = {{{escaped}}},")
    lines.append("}")
    return "\n".join(lines)
