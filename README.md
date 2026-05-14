# Desc2Cite

一个按工程分层组织的“自然语言描述 -> 学术论文引用”项目。

## 项目结构

```text
Desc2Cite/
├─ desc2cite/
│  ├─ application/      # 用例编排，负责串起整条流水线
│  ├─ domain/           # 领域模型与纯业务逻辑
│  ├─ infrastructure/   # 检索提供者、配置、样例数据等外部适配层
│  ├─ interfaces/       # CLI 等输入输出接口
│  ├─ bootstrap.py      # 依赖装配
│  └─ __init__.py
├─ docs/
├─ tests/
├─ pyproject.toml
└─ uv.lock
```

## 当前能力

1. 查询优化：从自然语言中提取关键词、短语和年份提示。
2. 学术检索：支持本地 JSON 语料检索，并预留 Crossref 远程检索。
3. 结果重排序：按标题覆盖率、年份、DOI 和元数据完整性重新打分。
4. 信息提取：标准化作者、题目、年份、期刊/会议等字段。
5. BibTeX 生成：输出可直接使用的 BibTeX。
6. 引用格式输出：支持 `apa`、`mla`、`plain`。

## 使用方式

命令行运行：

```bash
uv run python -m desc2cite.interfaces.cli.main "transformer paper attention is all you need"
```

输出 JSON：

```bash
uv run python -m desc2cite.interfaces.cli.main "bert pre-training paper from 2019" --json
```

启用远程 Crossref 检索：

```bash
uv run python -m desc2cite.interfaces.cli.main "paper about scholarly metadata and crossref" --remote --mailto you@example.com
```

启用 AI 查询改写：

```bash
$env:DESC2CITE_AI_API_KEY="your_api_key"
uv run python -m desc2cite.interfaces.cli.main "2017年那个提出纯注意力结构的transformer经典论文" --ai-rewrite --ai-base-url https://api.openai.com/v1 --ai-model gpt-4.1-mini
```

使用 MiniMax：

```bash
$env:MINIMAX_API_KEY="aaaaaaa"
uv run python -m desc2cite.interfaces.cli.main "2017年那个提出纯注意力结构的transformer经典论文" --ai-rewrite --ai-provider minimax --json
```

也可以使用安装后的脚本入口：

```bash
uv run desc2cite "transformer paper attention is all you need"
```

## 自定义语料

你可以传入自己的 JSON 语料文件：

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

运行时指定：

```bash
uv run python -m desc2cite.interfaces.cli.main "your natural language description" --corpus path/to/corpus.json
```

## 测试

```bash
uv run python -m unittest discover -s tests -v
```
