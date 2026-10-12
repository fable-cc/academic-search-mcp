# Research Paper MCP

**Give your AI agent the ability to search 187 million academic papers.**

An MCP server that lets Claude, Cursor, and any MCP-compatible agent search
[Crossref](https://www.crossref.org/) and [arXiv](https://arxiv.org/) — so it can
cite real papers instead of inventing them.

[![PyPI](https://img.shields.io/pypi/v/research-paper-mcp?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/research-paper-mcp/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![CI](https://github.com/fable-cc/research-paper-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/fable-cc/research-paper-mcp/actions/workflows/ci.yml)

**[English](#english) · [中文](#中文)**

---

## Why this exists

LLMs hallucinate citations. Ask any model for "papers on retrieval-augmented
generation" and you'll get a plausible-looking list where a third of the DOIs
don't resolve.

This MCP server fixes that by giving the agent a real retrieval tool. It queries
two open, legally-clean metadata sources and returns verifiable results:

| Source | Coverage | License |
|---|---|---|
| **Crossref** | 187M+ works across all disciplines | CC0 — free for commercial use |
| **arXiv** | 2.9M+ preprints (CS, math, physics, bio) | Open access |

No paywalled content. No scraping of restricted sources. Every result carries a
DOI or arXiv ID you can verify yourself.

## Install

```bash
pip install research-paper-mcp
```

That's it. No cloning, no manual dependency setup.

## Configure

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "research-paper": {
      "command": "python",
      "args": ["-m", "research_paper_mcp"]
    }
  }
}
```

### Claude Code

```bash
claude mcp add research-paper -- python -m research_paper_mcp
```

### Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "research-paper": {
      "command": "python",
      "args": ["-m", "research_paper_mcp"]
    }
  }
}
```

> Using a virtualenv? Replace `"python"` with the absolute path to that
> environment's interpreter.

## Tools

| Tool | What it does |
|---|---|
| `search_papers` | Cross-source search across Crossref + arXiv. Returns title, authors, abstract, citation count, DOI. |
| `get_paper` | Fetch full metadata for a single paper by DOI. |
| `get_references` | Get the reference list of a paper — useful for citation-graph traversal. |
| `search_arxiv_papers` | arXiv-only search, with category filters (e.g. `cs.CL`, `cs.LG`). |

## Example

Once configured, just ask your agent:

> Find me the 5 most-cited papers on retrieval-augmented generation published
> after 2022, and summarize what each one contributes.

The agent calls `search_papers`, gets real metadata back, and answers with
verifiable citations:

```
1. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks
   Lewis et al., 2020 · DOI: 10.48550/arXiv.2005.11401
   Cited by: 8,432
   → Introduces the RAG framework: a seq2seq model with a dense retriever...

2. Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection
   Asai et al., 2023 · DOI: 10.48550/arXiv.2310.11511
   Cited by: 1,205
   → Adds a self-reflection mechanism so the model decides when to retrieve...
```

## Use cases

- **Literature review** — map a research area without manually tabbing through
  search engines.
- **Fact-checking** — verify that a citation an LLM produced actually exists.
- **Citation-graph exploration** — walk backwards through references to find
  foundational work.
- **Writing assistance** — ground technical writing in real sources.

## Roadmap

- [ ] PubMed Central full-text retrieval
- [ ] Semantic Scholar API as a third source (citation context, not just counts)
- [ ] Local caching to avoid re-querying the same DOI
- [ ] BibTeX export

Have a use case that's missing? [Open an issue](https://github.com/fable-cc/research-paper-mcp/issues).

## Contributing

Issues and pull requests are welcome. For substantial changes, please open an
issue first to discuss the approach.

```bash
git clone https://github.com/fable-cc/research-paper-mcp
cd research-paper-mcp
pip install -e ".[dev]"
pytest
```

## License

MIT — see [LICENSE](LICENSE).

Data sources retain their own terms: Crossref metadata is CC0; arXiv content is
subject to arXiv's terms of use. This project only queries public metadata APIs
and does not redistribute paper full text.

---

## 中文

# Research Paper MCP

**让你的 AI Agent 能检索 1.87 亿篇学术论文。**

一个 MCP 服务，让 Claude、Cursor 以及任何支持 MCP 的 Agent 能够搜索
[Crossref](https://www.crossref.org/) 和 [arXiv](https://arxiv.org/) ——
让它引用真实存在的论文，而不是编造文献。

### 为什么需要它

大模型会虚构引用。随便问一个模型「关于检索增强生成的论文有哪些」，你会得到一份
看起来很合理、但其中三分之一的 DOI 根本打不开的清单。

这个 MCP 服务通过给 Agent 一个真实的检索工具来解决这个问题。它查询两个开放的、
无版权风险的元数据源，返回可核验的结果：

| 数据源 | 覆盖范围 | 授权 |
|---|---|---|
| **Crossref** | 1.87 亿篇跨学科论文 | CC0 — 免费商用 |
| **arXiv** | 290 万篇预印本（计算机、数学、物理、生物） | 开放获取 |

不涉及闭库内容，不抓取受限来源。每条结果都带 DOI 或 arXiv ID，你可以自行核验。

### 安装

```bash
pip install research-paper-mcp
```

不需要克隆仓库，不需要手动处理依赖。

### 配置 Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "research-paper": {
      "command": "python",
      "args": ["-m", "research_paper_mcp"]
    }
  }
}
```

> 如果你使用虚拟环境，请把 `"python"` 替换为该环境解释器的绝对路径。

### 提供的工具

| 工具 | 功能 |
|---|---|
| `search_papers` | 跨库搜索（Crossref + arXiv），返回标题、作者、摘要、引用数、DOI |
| `get_paper` | 通过 DOI 获取单篇论文详情 |
| `get_references` | 获取论文的参考文献列表，用于引用图谱遍历 |
| `search_arxiv_papers` | 专门搜索 arXiv 预印本，支持分类过滤（如 `cs.CL`、`cs.LG`） |

### 适用场景

- **文献综述** —— 不用手动在多个搜索站之间来回切换就能摸清一个研究领域。
- **事实核查** —— 验证大模型给出的引用是否真实存在。
- **引用图谱探索** —— 顺着参考文献回溯，找到奠基性工作。
- **写作辅助** —— 让技术写作建立在真实来源之上。

### 授权

MIT，详见 [LICENSE](LICENSE)。

数据源各自保留其条款：Crossref 元数据为 CC0；arXiv 内容受 arXiv 使用条款约束。
本项目仅查询公开的元数据 API，不重新分发论文全文。

---

<div align="center">

由 [景一 fable](https://fable-castle.com/) 构建 · GEO 与 AI 可见度
<br>
<sub>如果这个工具对你有用，给个 star 能让更多人找到它。</sub>

</div>
