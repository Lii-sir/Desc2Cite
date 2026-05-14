from __future__ import annotations

import re
from dataclasses import dataclass

from desc2cite.infrastructure.ai.errors import QueryRewriteAuthError, QueryRewriteRequestError, QueryRewriteTimeoutError


class QueryRewriter:
    def rewrite(self, description: str) -> str | None:
        raise NotImplementedError


@dataclass(slots=True)
class AiQueryRewriter(QueryRewriter):
    base_url: str
    api_key: str
    model: str
    timeout: float = 15.0

    def rewrite(self, description: str) -> str | None:
        try:
            from openai import APIConnectionError, APITimeoutError, APIStatusError, AuthenticationError, OpenAI
        except ImportError as error:
            raise QueryRewriteRequestError("openai SDK is not installed") from error

        client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout,
        )

        try:
            response = client.chat.completions.create(
                model=self.model,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a scholarly search query rewriter.\n"
                            "Your job is to convert a user's natural-language paper description into a short search query "
                            "for academic paper retrieval.\n"
                            "Rules:\n"
                            "1. Preserve all paper acronyms exactly as written, such as CAGrad, LoRA, BERT, RAG.\n"
                            "2. If you can identify the paper title with high confidence, output the exact English title "
                            "or the title plus 1-3 retrieval keywords.\n"
                            "3. If you are not sure of the exact title, do not invent authors, year, venue, DOI, or paper title.\n"
                            "4. Remove vague words such as: classic paper, famous paper, that paper, work, study, research, method.\n"
                            "5. Keep useful constraints from the input: acronym, title words, author names, year, task, domain.\n"
                            "6. Prefer concise retrieval-style keyword queries, not sentences.\n"
                            "7. Output only one plain-text query.\n"
                            "8. Do not explain anything.\n"
                            "9. Keep the query short, usually 6-12 tokens.\n"
                            "10. If the input is Chinese, rewrite it into concise English search keywords for English academic metadata.\n"
                            "11. If the input contains a year, preserve it.\n"
                            "12. If the input contains an acronym but little context, keep the acronym and add only the most likely "
                            "task or domain terms if they are strongly implied.\n"
                            "13. If uncertain, be conservative and keep more original terms instead of hallucinating.\n"
                            "Output format:\n"
                            "Only the query text, nothing else."
                        ),
                    },
                    {
                        "role": "user",
                        "content": description,
                    },
                ],
            )
        except AuthenticationError as error:
            raise QueryRewriteAuthError("MiniMax key 无效") from error
        except APIStatusError as error:
            if error.status_code in {401, 403}:
                raise QueryRewriteAuthError("MiniMax key 无效") from error
            raise QueryRewriteRequestError(f"AI query rewrite failed with HTTP {error.status_code}") from error
        except APITimeoutError as error:
            raise QueryRewriteTimeoutError("AI query rewrite request timed out") from error
        except APIConnectionError as error:
            raise QueryRewriteRequestError("AI query rewrite request failed") from error
        except Exception as error:
            raise QueryRewriteRequestError(f"AI query rewrite failed: {type(error).__name__}") from error

        try:
            content = response.choices[0].message.content or ""
        except (AttributeError, IndexError, TypeError) as error:
            raise QueryRewriteRequestError("AI query rewrite response is missing content") from error

        rewritten = _post_process_query(_strip_think_blocks(str(content)))
        return rewritten or None


def _strip_think_blocks(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()


def _post_process_query(text: str) -> str:
    cleaned = text.strip()
    cleaned = cleaned.replace("\n", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\b(classic|famous|seminal|paper|papers|work|study|research|method)\b", " ", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace("经典论文", " ")
    cleaned = cleaned.replace("经典", " ")
    cleaned = cleaned.replace("那篇", " ")
    cleaned = cleaned.replace("论文", " ")
    cleaned = cleaned.replace("文献", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
