# Architecture

## Flow

```text
User Description
  -> Query Optimizer
  -> Academic Search Engine
  -> Result Reranker
  -> Metadata Extractor
  -> BibTeX Generator
  -> Citation Formatter
```

## Layers

### `desc2cite.domain`

领域层只放纯业务对象和纯规则：

- `models.py`: 查询、论文、搜索结果、流水线结果
- `services/query_optimizer.py`: 查询优化
- `services/reranker.py`: 重排序
- `services/metadata_extractor.py`: 元数据提取与 BibTeX key 生成
- `services/bibtex_generator.py`: BibTeX 生成
- `services/citation_formatter.py`: 引用格式输出

### `desc2cite.application`

应用层负责编排完整用例：

- `services/desc_to_cite_service.py`: 串联整条流水线，不关心具体搜索来源

### `desc2cite.infrastructure`

基础设施层负责外部依赖与适配：

- `config.py`: 运行配置
- `search/academic_search_engine.py`: 搜索引擎聚合器
- `search/providers/local_corpus_provider.py`: 本地语料检索
- `search/providers/crossref_provider.py`: Crossref 远程检索
- `data/sample_corpus.json`: 本地示例数据

### `desc2cite.interfaces`

接口层负责输入输出：

- `cli/main.py`: 命令行入口

### `desc2cite/bootstrap.py`

负责装配依赖，把 application 和 infrastructure 接起来。

## Extension Points

后续如果你要继续做成完整项目，建议按这个方向扩展：

1. 新增 `interfaces/api/`，提供 FastAPI 接口。
2. 在 `infrastructure/search/providers/` 下增加 Semantic Scholar、OpenAlex、arXiv 适配器。
3. 把重排序从规则打分替换成 embedding 或 cross-encoder 模型。
4. 新增 `application/dto/` 与 `application/commands/`，把输入输出对象进一步标准化。
5. 补充 `tests/unit/`、`tests/integration/` 分层测试。
