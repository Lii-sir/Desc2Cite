from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv() -> None:
    dotenv_path = Path(__file__).resolve().parents[2] / ".env"
    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_dotenv()


@dataclass(slots=True)
class SearchSettings:
    corpus_path: Path
    enable_remote: bool = False
    crossref_mailto: str | None = None
    enable_ai_rewrite: bool = False
    ai_provider: str | None = None
    ai_base_url: str | None = None
    ai_api_key: str | None = None
    ai_model: str | None = None


def default_search_settings(
    corpus_path: str | None = None,
    enable_remote: bool = False,
    crossref_mailto: str | None = None,
    enable_ai_rewrite: bool = False,
    ai_provider: str | None = None,
    ai_base_url: str | None = None,
    ai_api_key: str | None = None,
    ai_model: str | None = None,
) -> SearchSettings:
    default_corpus = Path(__file__).resolve().parent / "data" / "sample_corpus.json"
    provider = (ai_provider or os.getenv("DESC2CITE_AI_PROVIDER") or "").strip().casefold() or None

    minimax_base_url = os.getenv("MINIMAX_BASE_URL") or "https://api.minimaxi.com/v1"
    minimax_api_key = os.getenv("MINIMAX_API_KEY")
    minimax_model = os.getenv("MINIMAX_MODEL") or "MiniMax-M2.7"

    resolved_base_url = ai_base_url or os.getenv("DESC2CITE_AI_BASE_URL") or os.getenv("OPENAI_BASE_URL")
    resolved_api_key = ai_api_key or os.getenv("DESC2CITE_AI_API_KEY") or os.getenv("OPENAI_API_KEY")
    resolved_model = ai_model or os.getenv("DESC2CITE_AI_MODEL") or "gpt-4.1-mini"

    if provider == "minimax":
        resolved_base_url = ai_base_url or os.getenv("DESC2CITE_AI_BASE_URL") or minimax_base_url
        resolved_api_key = ai_api_key or os.getenv("DESC2CITE_AI_API_KEY") or minimax_api_key
        resolved_model = ai_model or os.getenv("DESC2CITE_AI_MODEL") or minimax_model

    return SearchSettings(
        corpus_path=Path(corpus_path) if corpus_path else default_corpus,
        enable_remote=enable_remote,
        crossref_mailto=crossref_mailto,
        enable_ai_rewrite=enable_ai_rewrite,
        ai_provider=provider,
        ai_base_url=resolved_base_url,
        ai_api_key=resolved_api_key,
        ai_model=resolved_model,
    )
