# Academic MCP Server

让 AI Agent 搜索和查询学术论文的 MCP（Model Context Protocol）服务。

## 提供的工具

| 工具 | 功能 |
|------|------|
| `search_papers` | 跨库搜索（Crossref + arXiv），返回标题、作者、摘要、引用数 |
| `get_paper` | 通过 DOI 获取单篇论文详情 |
| `get_references` | 获取论文的参考文献列表 |
| `search_arxiv_papers` | 专门搜索 arXiv 预印本 |

## 数据源

- **Crossref**（CC0）：1.87 亿篇论文元数据，免费商用
- **arXiv**：290 万篇预印本，免费查询
- 无闭库内容、无版权风险

## 安装

```bash
cd /path/to/this/directory
pip install -r requirements.txt
```

## 测试运行

```bash
python server.py
```

## 接入 Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "academic": {
      "command": "python3",
      "args": ["/Users/jingyi/Doubao/chats/2026-09-10/new-chat-6/server.py"]
    }
  }
}
```

重启 Claude Desktop 后，Agent 就可以说"帮我搜一下 XXX 论文"了。

## 接入其他 MCP 客户端

任何支持 MCP 协议的客户端（Cursor、Windsurf、Cline 等）都可以用同样的 stdio 方式启动。

## 下一步扩展

- [ ] 接入 PubMed Central（生物医学全文）
- [ ] 接入 DOAJ（1100 万篇 OA 论文）
- [ ] 接入 Semantic Scholar（引用图谱）
- [ ] 添加全文获取（仅 OA 内容）
- [ ] 改为 HTTP 模式支持远程调用
