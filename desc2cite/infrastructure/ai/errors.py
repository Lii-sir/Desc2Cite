from __future__ import annotations


class QueryRewriteError(Exception):
    """Base exception for AI query rewrite failures."""


class QueryRewriteAuthError(QueryRewriteError):
    """Raised when the AI provider rejects authentication."""


class QueryRewriteRequestError(QueryRewriteError):
    """Raised when the AI provider request fails for non-auth reasons."""


class QueryRewriteTimeoutError(QueryRewriteRequestError):
    """Raised when the AI provider request times out."""
