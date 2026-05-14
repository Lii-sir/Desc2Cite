from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from desc2cite.application.services.desc_to_cite_service import DescToCiteService
from desc2cite.bootstrap import build_desc_to_cite_service
from desc2cite.domain.services import optimize_query
from desc2cite.infrastructure.ai import QueryRewriteAuthError
from desc2cite.infrastructure.ai.query_rewriter import _post_process_query
from desc2cite.infrastructure.config import default_search_settings
from desc2cite.infrastructure.search import AcademicSearchEngine, LocalCorpusSearchProvider

_ROOT = Path(__file__).resolve().parents[1]
_CORPUS_PATH = _ROOT / "desc2cite" / "infrastructure" / "data" / "sample_corpus.json"


class StubQueryRewriter:
    def rewrite(self, description: str) -> str | None:
        if "\u6ce8\u610f\u529b" in description or "transformer" in description.casefold():
            return "attention is all you need transformer 2017"
        return None


class AuthFailingQueryRewriter:
    def rewrite(self, description: str) -> str | None:
        raise QueryRewriteAuthError("MiniMax key 无效")


class QueryOptimizerTests(unittest.TestCase):
    def test_extracts_year_and_candidate_queries(self) -> None:
        query = optimize_query('find the 2017 paper "Attention Is All You Need"')
        self.assertEqual(query.year_hint, 2017)
        self.assertIn("Attention Is All You Need", query.candidate_queries)

    def test_minimax_provider_uses_minimax_env_defaults(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "MINIMAX_API_KEY": "aaaaaaa",
                "MINIMAX_BASE_URL": "https://api.minimaxi.com/v1",
                "MINIMAX_MODEL": "MiniMax-M2.7",
                "DESC2CITE_AI_API_KEY": "",
                "DESC2CITE_AI_BASE_URL": "",
                "DESC2CITE_AI_MODEL": "",
            },
            clear=False,
        ):
            settings = default_search_settings(enable_ai_rewrite=True, ai_provider="minimax")
        self.assertEqual(settings.ai_provider, "minimax")
        self.assertEqual(settings.ai_api_key, "aaaaaaa")
        self.assertEqual(settings.ai_base_url, "https://api.minimaxi.com/v1")
        self.assertEqual(settings.ai_model, "MiniMax-M2.7")

    def test_post_process_query_removes_noise_terms(self) -> None:
        cleaned = _post_process_query("CAGrad classic paper multi-task learning 经典论文")
        self.assertEqual(cleaned, "CAGrad multi-task learning")


class PipelineTests(unittest.TestCase):
    def test_pipeline_returns_bibtex(self) -> None:
        service = build_desc_to_cite_service()
        result = service.run("transformer paper attention is all you need", style="apa")
        self.assertIsNotNone(result.chosen)
        self.assertIn("Attention Is All You Need", result.chosen.record.title)
        self.assertIsNotNone(result.bibtex)
        self.assertIn("@inproceedings", result.bibtex)

    def test_pipeline_supports_ai_rewritten_chinese_description(self) -> None:
        service = DescToCiteService(
            search_engine=AcademicSearchEngine(
                providers=[
                    LocalCorpusSearchProvider(corpus_path=_CORPUS_PATH)
                ]
            ),
            query_rewriter=StubQueryRewriter(),
        )
        result = service.run(
            "2017年那篇提出纯注意力结构的transformer经典论文",
            style="apa",
        )
        self.assertIsNotNone(result.chosen)
        self.assertEqual(result.query.rewritten_text, "attention is all you need transformer 2017")
        self.assertIn("Attention Is All You Need", result.chosen.record.title)

    def test_pipeline_raises_auth_error_for_invalid_ai_key(self) -> None:
        service = DescToCiteService(
            search_engine=AcademicSearchEngine(
                providers=[
                    LocalCorpusSearchProvider(corpus_path=_CORPUS_PATH)
                ]
            ),
            query_rewriter=AuthFailingQueryRewriter(),
        )
        with self.assertRaises(QueryRewriteAuthError):
            service.run("2017年那篇提出纯注意力结构的transformer经典论文", style="apa")

    def test_can_write_generated_bibtex_to_file(self) -> None:
        service = build_desc_to_cite_service()
        result = service.run("transformer paper attention is all you need", style="apa")
        output_path = _ROOT / "tests" / "artifacts" / "attention.bib"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result.bibtex + "\n", encoding="utf-8")
        self.assertTrue(output_path.exists())
        self.assertIn("@inproceedings", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
