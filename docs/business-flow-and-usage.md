# Desc2Cite 业务流程与使用说明

## 1. 项目目标

Desc2Cite 用来把一段自然语言描述转换成结构化的论文引用结果。

典型输入：

```text
transformer paper attention is all you need
```

典型输出：

1. 最匹配的论文信息
2. 格式化引用文本
3. BibTeX
4. 候选检索结果及评分

---

## 2. 当前业务流程

当前实现的主流程由 [desc2cite/application/services/desc_to_cite_service.py](D:/python_programs/LXD_project/Desc2Cite/desc2cite/application/services/desc_to_cite_service.py) 负责串联，整体流程如下：

```text
用户输入自然语言描述
    -> 查询优化
    -> 学术检索
    -> 结果重排序
    -> 论文信息提取
    -> BibTeX 生成
    -> 引用格式输出
```

### 2.1 用户输入

用户输入一段对目标论文的自然语言描述，可以包含：

1. 论文标题中的关键词
2. 作者信息
3. 年份
4. 研究主题
5. 会议或期刊线索

例如：

```text
find the 2017 transformer paper "Attention Is All You Need"
```

### 2.2 查询优化

对应实现：

- [desc2cite/domain/services/query_optimizer.py](D:/python_programs/LXD_project/Desc2Cite/desc2cite/domain/services/query_optimizer.py)

这个阶段会做这些事：

1. 归一化输入文本
2. 分词
3. 去掉一部分停用词
4. 提取引号中的短语
5. 识别年份提示
6. 生成若干候选查询文本

输出对象是 `SearchQuery`，包含：

1. 原始输入
2. 归一化文本
3. 关键词 token
4. 候选短语
5. 候选查询
6. 年份提示

### 2.3 学术检索

对应实现：

- [desc2cite/bootstrap.py](D:/python_programs/LXD_project/Desc2Cite/desc2cite/bootstrap.py)
- [desc2cite/infrastructure/search/academic_search_engine.py](D:/python_programs/LXD_project/Desc2Cite/desc2cite/infrastructure/search/academic_search_engine.py)
- [desc2cite/infrastructure/search/providers/local_corpus_provider.py](D:/python_programs/LXD_project/Desc2Cite/desc2cite/infrastructure/search/providers/local_corpus_provider.py)
- [desc2cite/infrastructure/search/providers/crossref_provider.py](D:/python_programs/LXD_project/Desc2Cite/desc2cite/infrastructure/search/providers/crossref_provider.py)

当前支持两类检索源：

1. 本地 JSON 语料
2. 可选的 Crossref 远程检索

默认情况下，系统会使用本地样例语料：

- [desc2cite/infrastructure/data/sample_corpus.json](D:/python_programs/LXD_project/Desc2Cite/desc2cite/infrastructure/data/sample_corpus.json)

本地检索的评分依据主要包括：

1. 标题与查询词的重合度
2. 摘要与查询词的重合度
3. 作者字段重合度
4. 期刊/会议字段重合度
5. 是否命中短语
6. 是否命中年份

### 2.4 结果重排序

对应实现：

- [desc2cite/domain/services/reranker.py](D:/python_programs/LXD_project/Desc2Cite/desc2cite/domain/services/reranker.py)

这个阶段会在初始检索结果基础上再次打分，主要增加这些偏好：

1. 标题 token 覆盖率更高的结果优先
2. 带 DOI 的结果优先
3. 元数据更完整的结果优先
4. 年份匹配的结果优先

最终会选出得分最高的一条作为主结果。

### 2.5 论文信息提取

对应实现：

- [desc2cite/domain/services/metadata_extractor.py](D:/python_programs/LXD_project/Desc2Cite/desc2cite/domain/services/metadata_extractor.py)

这个阶段会把论文记录整理成适合生成 BibTeX 的字段，包括：

1. `title`
2. `author`
3. `year`
4. `journal` 或 `booktitle`
5. `publisher`
6. `volume`
7. `number`
8. `pages`
9. `doi`
10. `url`

同时还会自动生成一个 BibTeX key，例如：

```text
vaswani2017attention
```

### 2.6 BibTeX 生成

对应实现：

- [desc2cite/domain/services/bibtex_generator.py](D:/python_programs/LXD_project/Desc2Cite/desc2cite/domain/services/bibtex_generator.py)

这个阶段会根据论文类型和元数据字段生成 BibTeX 文本，例如：

```bibtex
@inproceedings{vaswani2017attention,
  title = {Attention Is All You Need},
  author = {Ashish Vaswani and Noam Shazeer and Niki Parmar and Jakob Uszkoreit and Llion Jones and Aidan N. Gomez and Lukasz Kaiser and Illia Polosukhin},
  year = {2017},
  booktitle = {Advances in Neural Information Processing Systems},
  publisher = {Curran Associates, Inc.},
  doi = {10.48550/arXiv.1706.03762},
  url = {https://arxiv.org/abs/1706.03762},
}
```

### 2.7 引用格式输出

对应实现：

- [desc2cite/domain/services/citation_formatter.py](D:/python_programs/LXD_project/Desc2Cite/desc2cite/domain/services/citation_formatter.py)

当前支持三种引用格式：

1. `apa`
2. `mla`
3. `plain`

输出的是一段可直接展示或复制的引用文本。

---

## 3. 当前目录中各层的职责

### `desc2cite/domain`

负责纯业务逻辑，不依赖外部输入输出。

### `desc2cite/application`

负责把各个业务步骤按顺序串起来，形成完整用例。

### `desc2cite/infrastructure`

负责外部依赖与适配，比如本地语料、Crossref 检索、搜索引擎装配。

### `desc2cite/interfaces`

负责对外暴露使用方式，当前主要是 CLI。

---

## 4. 使用方式

当前推荐使用 `uv`。

### 4.1 直接运行命令行

```bash
uv run python -m desc2cite.interfaces.cli.main "transformer paper attention is all you need"
```

输出内容包括：

1. 选中的论文标题
2. 格式化引用
3. BibTeX
4. Top matches 候选结果

### 4.2 输出 JSON

如果你希望拿到更适合程序处理的结果，可以加 `--json`：

```bash
uv run python -m desc2cite.interfaces.cli.main "bert pre-training paper from 2019" --json
```

JSON 输出中主要包含：

1. `query`
2. `chosen`
3. `citation`
4. `bibtex`
5. `matches`

### 4.3 指定引用格式

```bash
uv run python -m desc2cite.interfaces.cli.main "attention is all you need" --style apa
uv run python -m desc2cite.interfaces.cli.main "attention is all you need" --style mla
uv run python -m desc2cite.interfaces.cli.main "attention is all you need" --style plain
```

### 4.4 指定候选数量

```bash
uv run python -m desc2cite.interfaces.cli.main "attention is all you need" --top-k 10
```

### 4.5 使用自定义语料

如果你有自己的论文数据，可以传入自己的 JSON 文件：

```bash
uv run python -m desc2cite.interfaces.cli.main "your natural language description" --corpus path/to/corpus.json
```

语料 JSON 结构示例：

```json
[
  {
    "title": "Paper Title",
    "authors": ["First Author", "Second Author"],
    "year": 2024,
    "venue": "Conference Name",
    "abstract": "Paper abstract",
    "doi": "10.xxxx/xxxxx",
    "url": "https://example.org/paper",
    "entry_type": "inproceedings"
  }
]
```

### 4.6 启用 Crossref 远程检索

```bash
uv run python -m desc2cite.interfaces.cli.main "paper about scholarly metadata and crossref" --remote --mailto you@example.com
```

说明：

1. `--remote` 表示启用 Crossref
2. `--mailto` 用于给 Crossref 提供联系邮箱

### 4.7 使用安装后的脚本入口

如果环境里已经安装了项目，也可以直接使用脚本入口：

```bash
uv run desc2cite "transformer paper attention is all you need"
```

---

## 5. 返回结果说明

当前 CLI 会返回两种形式。

### 5.1 普通文本模式

会输出：

1. `Chosen paper`
2. 指定格式的引用文本
3. BibTeX
4. `Top matches`

### 5.2 JSON 模式

会输出：

1. `query`
2. `chosen`
3. `citation`
4. `bibtex`
5. `matches`

其中 `matches` 是候选结果列表，可用于：

1. 调试检索效果
2. 给后续前端展示候选项
3. 分析排序逻辑是否合理

---

## 6. 测试方式

运行测试：

```bash
uv run python -m unittest discover -s tests -v
```

当前测试覆盖了：

1. 查询优化中的年份与候选查询提取
2. 整条流水线是否能正确返回 BibTeX

测试文件：

- [tests/test_pipeline.py](D:/python_programs/LXD_project/Desc2Cite/tests/test_pipeline.py)

---

## 7. 当前实现的边界

当前版本已经具备完整的端到端流程，但仍然属于第一版实现。

目前的边界包括：

1. 默认检索主要依赖本地样例语料
2. 重排序目前是规则打分，不是模型打分
3. 引用格式支持还比较基础
4. 还没有 HTTP API 和前端页面

如果后续继续扩展，比较自然的方向是：

1. 增加 API 层
2. 接入更多学术搜索源
3. 引入 embedding 或 reranker 模型
4. 增加更完整的引用格式支持
