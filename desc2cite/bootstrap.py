from __future__ import annotations

from desc2cite.application import DescToCiteService
from desc2cite.infrastructure.ai import AiQueryRewriter
from desc2cite.infrastructure.config import default_search_settings
from desc2cite.infrastructure.search import (
    AcademicSearchEngine,
    ArxivSearchProvider,
    CrossrefSearchProvider,
    LocalCorpusSearchProvider,
    OpenAlexSearchProvider,
    SemanticScholarSearchProvider,
)


def build_desc_to_cite_service(
    corpus_path: str | None = None,
    enable_remote: bool = False,
    crossref_mailto: str | None = None,
    enable_ai_rewrite: bool = False,
    ai_provider: str | None = None,
    ai_base_url: str | None = None,
    ai_api_key: str | None = None,
    ai_model: str | None = None,
) -> DescToCiteService:
    settings = default_search_settings(
        corpus_path=corpus_path,
        enable_remote=enable_remote,
        crossref_mailto=crossref_mailto,
        enable_ai_rewrite=enable_ai_rewrite,
        ai_provider=ai_provider,
        ai_base_url=ai_base_url,
        ai_api_key=ai_api_key,
        ai_model=ai_model,
    )
    providers = [LocalCorpusSearchProvider(corpus_path=settings.corpus_path)]
    if settings.enable_remote:
        providers.insert(0, SemanticScholarSearchProvider())
        providers.insert(0, OpenAlexSearchProvider(mailto=settings.crossref_mailto))
        providers.insert(0, CrossrefSearchProvider(mailto=settings.crossref_mailto))
        providers.insert(0, ArxivSearchProvider())
    query_rewriter = None
    if settings.enable_ai_rewrite and settings.ai_base_url and settings.ai_api_key and settings.ai_model:
        query_rewriter = AiQueryRewriter(
            base_url=settings.ai_base_url,
            api_key=settings.ai_api_key,
            model=settings.ai_model,
        )
    return DescToCiteService(
        search_engine=AcademicSearchEngine(providers=providers),
        query_rewriter=query_rewriter,
    )
