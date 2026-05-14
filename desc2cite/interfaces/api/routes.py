from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from desc2cite.bootstrap import build_desc_to_cite_service
from desc2cite.infrastructure.ai import QueryRewriteAuthError, QueryRewriteRequestError, QueryRewriteTimeoutError

router = APIRouter(prefix="/api")


class SearchRequest(BaseModel):
    description: str = Field(..., min_length=1)
    style: str = Field(default="apa")
    top_k: int = Field(default=5, ge=1, le=20)
    remote: bool = False
    mailto: str | None = None
    ai_rewrite: bool = False
    ai_provider: str | None = None
    ai_base_url: str | None = None
    ai_model: str | None = None


@router.post("/search")
def search(request: SearchRequest) -> dict:
    service = build_desc_to_cite_service(
        enable_remote=request.remote,
        crossref_mailto=request.mailto,
        enable_ai_rewrite=request.ai_rewrite,
        ai_provider=request.ai_provider,
        ai_base_url=request.ai_base_url,
        ai_model=request.ai_model,
    )

    try:
        result = service.run(
            description=request.description,
            top_k=request.top_k,
            style=request.style,
        )
    except QueryRewriteAuthError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    except QueryRewriteTimeoutError as error:
        raise HTTPException(status_code=504, detail=str(error)) from error
    except QueryRewriteRequestError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    return {
        "query": {
            "original": result.query.original_text,
            "tokens": result.query.tokens,
            "candidate_queries": result.query.candidate_queries,
            "rewritten_text": result.query.rewritten_text,
            "year_hint": result.query.year_hint,
        },
        "chosen": None
        if result.chosen is None
        else {
            "title": result.chosen.record.title,
            "authors": result.chosen.record.authors,
            "year": result.chosen.record.year,
            "venue": result.chosen.record.venue,
            "doi": result.chosen.record.doi,
            "url": result.chosen.record.url,
            "source": result.chosen.source,
            "score": round(result.chosen.score, 4),
        },
        "citation": result.formatted_citation,
        "bibtex": result.bibtex,
        "matches": [
            {
                "title": match.record.title,
                "authors": match.record.authors,
                "year": match.record.year,
                "venue": match.record.venue,
                "doi": match.record.doi,
                "url": match.record.url,
                "score": round(match.score, 4),
                "source": match.source,
                "reasons": match.reasons,
            }
            for match in result.matches
        ],
    }
