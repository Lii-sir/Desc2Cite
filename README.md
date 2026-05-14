# Desc2Cite

一个按工程分层组织的“自然语言描述 -> 学术论文引用”项目。

## 项目结构

```text
Desc2Cite/
├─ desc2cite/
│  ├─ application/      # 用例编排，负责串起整条流水线
│  ├─ domain/           # 领域模型与纯业务逻辑
│  ├─ infrastructure/   # 搜索源、AI 改写、配置与样例数据
│  ├─ interfaces/       # CLI / API / Web 接口层
│  ├─ bootstrap.py      # 依赖装配
│  └─ __init__.py
├─ docs/
├─ output/
├─ tests/
├─ pyproject.toml
└─ uv.lock
```

## 当前能力

1. 查询优化：从自然语言中提取关键词、短语和年份提示。
2. AI 改写：支持通过 OpenAI 兼容接口接入 MiniMax，把中文描述改写成检索 query。
3. 学术检索：支持本地 JSON 语料、arXiv、Crossref、OpenAlex、Semantic Scholar。
4. 结果重排序：按标题覆盖率、缩写命中、年份、DOI 和元数据完整性打分。
5. BibTeX 生成：输出可直接使用的 BibTeX。
6. 引用格式输出：支持 `apa`、`mla`、`plain`。
7. Web 界面：支持在浏览器中输入描述并查看候选结果、引用文本和 BibTeX。

## CLI 使用方式

基础命令：

```bash
uv run python -m desc2cite.interfaces.cli.main "transformer paper attention is all you need"
```

输出 JSON：

```bash
uv run python -m desc2cite.interfaces.cli.main "bert pre-training paper from 2019" --json
```

开启联网搜索：

```bash
uv run python -m desc2cite.interfaces.cli.main "CAGrad" --remote --json
```

启用 AI 改写：

```bash
uv run python -m desc2cite.interfaces.cli.main "2017年那个提出纯注意力结构的transformer经典论文" --ai-rewrite --ai-provider minimax --json
```

联网搜索 + AI 改写 + 保存 BibTeX：

```bash
uv run python -m desc2cite.interfaces.cli.main "CAGrad经典论文" --ai-rewrite --ai-provider minimax --remote --save-bib output\cagrad.bib --json
```

也可以使用虚拟环境里的 Python：

```bash
.\.venv\Scripts\python.exe -m desc2cite.interfaces.cli.main "CAGrad" --remote --json
```

## Web 启动方式

启动 Web 服务：

```bash
uv run python -m desc2cite.interfaces.web.main
```

启动后在浏览器打开：

```text
http://127.0.0.1:8000
```

Web 页面支持：

1. 输入论文描述
2. 勾选联网搜索
3. 勾选 AI 改写
4. 选择引用格式
5. 查看主结果、候选结果、引用文本和 BibTeX
6. 一键复制 BibTeX

## 如何配置自己的 API

项目现在支持通过 `.env` 或 PowerShell 环境变量配置你自己的 AI 接口。

### 方式一：修改项目根目录 `.env`

项目会自动读取根目录的 `.env` 文件。

如果你使用 MiniMax：

```env
MINIMAX_API_KEY=你的真实key
MINIMAX_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_MODEL=MiniMax-M2.7

DESC2CITE_AI_PROVIDER=minimax
DESC2CITE_AI_API_KEY=你的真实key
DESC2CITE_AI_BASE_URL=https://api.minimaxi.com/v1
DESC2CITE_AI_MODEL=MiniMax-M2.7
```

改完后可以直接运行：

```bash
uv run python -m desc2cite.interfaces.cli.main "CAGrad经典论文" --ai-rewrite --ai-provider minimax --remote --json
```

或者启动 Web：

```bash
uv run python -m desc2cite.interfaces.web.main
```

### 方式二：在 PowerShell 中临时设置

如果你不想改 `.env`，也可以只在当前终端里设置：

```powershell
$env:DESC2CITE_AI_PROVIDER="minimax"
$env:DESC2CITE_AI_API_KEY="你的真实key"
$env:DESC2CITE_AI_BASE_URL="https://api.minimaxi.com/v1"
$env:DESC2CITE_AI_MODEL="MiniMax-M2.7"
```

然后再运行命令：

```powershell
uv run python -m desc2cite.interfaces.cli.main "2017年那个提出纯注意力结构的transformer经典论文" --ai-rewrite --remote --json
```

### 如果你使用别的 OpenAI 兼容接口

如果你不是用 MiniMax，而是其他兼容 `chat/completions` 的服务，可以改成：

```powershell
$env:DESC2CITE_AI_PROVIDER="openai"
$env:DESC2CITE_AI_API_KEY="你的真实key"
$env:DESC2CITE_AI_BASE_URL="你的兼容接口地址"
$env:DESC2CITE_AI_MODEL="你的模型名"
```

例如：

```powershell
$env:DESC2CITE_AI_PROVIDER="openai"
$env:DESC2CITE_AI_API_KEY="your_key"
$env:DESC2CITE_AI_BASE_URL="https://api.openai.com/v1"
$env:DESC2CITE_AI_MODEL="gpt-4.1-mini"
```

### 如何判断配置成功

运行下面这条命令：

```bash
uv run python -m desc2cite.interfaces.cli.main "CAGrad经典论文" --ai-rewrite --remote --json
```

如果输出里出现：

```json
"rewritten_text": "..."
```

而不是：

```json
"rewritten_text": null
```

说明 AI 改写已经真正生效。

### 常见问题

1. `MiniMax key 无效`
   说明 key 错误，或者不是该接口可用的 key。
2. `AI query rewrite failed with HTTP 404`
   通常说明 `BASE_URL` 配错了。
3. `AI query rewrite request timed out`
   说明接口超时，可能是网络问题，也可能是服务响应慢。

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

运行测试：

```bash
uv run python -m unittest discover -s tests -v
```

## 相关文档

- [docs/architecture.md](D:/python_programs/LXD_project/Desc2Cite/docs/architecture.md)
- [docs/business-flow-and-usage.md](D:/python_programs/LXD_project/Desc2Cite/docs/business-flow-and-usage.md)
- [docs/minimax-setup.md](D:/python_programs/LXD_project/Desc2Cite/docs/minimax-setup.md)
