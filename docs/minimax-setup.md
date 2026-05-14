# MiniMax 接入说明

当前项目已经支持通过 OpenAI 兼容接口接入 MiniMax 做查询改写。

## 推荐配置

先在环境变量里配置：

```powershell
$env:MINIMAX_API_KEY="aaaaaaa"
$env:MINIMAX_BASE_URL="https://api.minimaxi.com/v1"
$env:MINIMAX_MODEL="MiniMax-M2.7"
```

然后运行：

```powershell
uv run python -m desc2cite.interfaces.cli.main "2017年那个提出纯注意力结构的transformer经典论文" --ai-rewrite --ai-provider minimax --json
```

## 也可以使用 Desc2Cite 自己的环境变量名

```powershell
$env:DESC2CITE_AI_PROVIDER="minimax"
$env:DESC2CITE_AI_API_KEY="aaaaaaa"
$env:DESC2CITE_AI_BASE_URL="https://api.minimaxi.com/v1"
$env:DESC2CITE_AI_MODEL="MiniMax-M2.7"
```

## 说明

1. `MINIMAX_API_KEY` 和 `DESC2CITE_AI_API_KEY` 都可以使用。
2. 如果指定了 `--ai-provider minimax`，项目会优先按 MiniMax 的默认配置解析。
3. 当前只把 MiniMax 用在“中文描述 -> 检索查询改写”这一步，后面的检索和 BibTeX 生成流程保持不变。
