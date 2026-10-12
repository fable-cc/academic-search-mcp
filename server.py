"""
research-paper-mcp - 学术文献检索 MCP 服务
通过 MCP 协议让 AI Agent 搜索和查询学术论文。

数据源（均为开放元数据，无版权风险）：
- Crossref (CC0): 1.87 亿篇跨学科论文元数据
- arXiv: 290 万篇预印本（计算机、数学、物理、生物）

启动方式（任选其一）：
  research-paper-mcp            # pip 安装后
  python -m research_paper_mcp  # 模块方式
  python server.py              # 直接运行本文件

MCP 客户端配置：
  {"mcpServers": {"research-paper": {"command": "python", "args": ["-m", "research_paper_mcp"]}}}

注意：PubMed Central 全文检索为规划中功能，当前尚未实现（见 PMC_API 常量注释）。
"""

import re
import xml.etree.ElementTree as ET
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# ---------- 初始化 ----------
mcp = FastMCP("academic-search")

# Crossref polite pool (填你的邮箱可以获得更快的速率)
CROSSREF_MAILTO = "academic-mcp@example.com"
CROSSREF_API = "https://api.crossref.org/works"
ARXIV_API = "https://export.arxiv.org/api/query"
# 预留：PMC 全文检索尚未实现。如需启用，请新增对应 @mcp.tool 后再在
# 上方 docstring 的「数据源」列表中恢复 PubMed Central 这一行。
PMC_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# 常用请求头
HEADERS = {
    "User-Agent": f"AcademicMCP/1.0 (mailto:{CROSSREF_MAILTO})",
}


# ---------- 工具函数 ----------

def clean_jats(xml_text: str | None) -> str:
    """清洗 JATS XML 格式的摘要，只保留纯文本。"""
    if not xml_text:
        return "（无摘要）"
    # 去掉所有 XML 标签
    text = re.sub(r"<[^>]+>", "", xml_text)
    # 折叠空白
    text = re.sub(r"\s+", " ", text).strip()
    return text if text else "（无摘要）"


def format_authors(author_list: list[dict]) -> str:
    """把 Crossref 作者列表格式化为 '姓, 名; 姓, 名' 字符串。"""
    names = []
    for a in author_list[:10]:  # 最多显示前 10 位
        given = a.get("given", "")
        family = a.get("family", "")
        if given and family:
            names.append(f"{family} {given}")
        elif family:
            names.append(family)
    if len(author_list) > 10:
        names.append("et al.")
    return "; ".join(names) if names else "（未知作者）"


def format_crossref_item(item: dict) -> dict:
    """把 Crossref 单条结果格式化为干净的字典。"""
    doi = item.get("DOI", "")
    title = (item.get("title") or ["（无标题）"])[0]
    container = (item.get("container-title") or [""])[0]
    year = None
    for key in ["published-print", "published-online", "issued", "created"]:
        if key in item and item[key].get("date-parts"):
            year = item[key]["date-parts"][0][0]
            break
    abstract = clean_jats(item.get("abstract"))
    authors = format_authors(item.get("author", []))
    url = item.get("URL", f"https://doi.org/{doi}")
    cited_by = item.get("is-referenced-by-count", 0)
    return {
        "doi": doi,
        "title": title,
        "authors": authors,
        "year": year,
        "venue": container,
        "abstract": abstract,
        "url": url,
        "cited_by": cited_by,
    }


def format_arxiv_entry(entry: dict) -> dict:
    """把 arXiv Atom 条目格式化为干净的字典。"""
    return {
        "arxiv_id": entry.get("id", "").split("/abs/")[-1],
        "title": entry.get("title", "").strip().replace("\n", " "),
        "authors": ", ".join(entry.get("authors", [])),
        "published": entry.get("published", "")[:10],
        "abstract": entry.get("summary", "").strip().replace("\n", " ")[:500],
        "categories": ", ".join(entry.get("categories", [])),
        "url": entry.get("id", ""),
    }


# ---------- API 调用 ----------

async def search_crossref(
    query: str, limit: int = 10, _client: httpx.AsyncClient | None = None
) -> list[dict]:
    """调用 Crossref API 搜索论文。"""
    params = {
        "query": query,
        "rows": limit,
        "select": "DOI,title,author,container-title,published-print,published-online,issued,created,abstract,URL,is-referenced-by-count,type",
        "mailto": CROSSREF_MAILTO,
        "sort": "relevance",
    }
    async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
        resp = await client.get(CROSSREF_API, params=params)
        resp.raise_for_status()
        items = resp.json()["message"].get("items", [])
        return [format_crossref_item(item) for item in items]


async def search_arxiv(
    query: str, limit: int = 10
) -> list[dict]:
    """调用 arXiv API 搜索预印本。"""
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
        "sortBy": "relevance",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(ARXIV_API, params=params)
        resp.raise_for_status()
        return parse_arxiv_xml(resp.text)


def parse_arxiv_xml(xml_text: str) -> list[dict]:
    """解析 arXiv 返回的 Atom XML。"""
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_text)
    results = []
    for entry in root.findall("atom:entry", ns):
        authors = [
            a.find("atom:name", ns).text
            for a in entry.findall("atom:author", ns)
            if a.find("atom:name", ns) is not None
        ]
        categories = [
            c.attrib.get("term", "")
            for c in entry.findall("atom:category", ns)
        ]
        results.append({
            "id": entry.find("atom:id", ns).text or "",
            "title": (entry.find("atom:title", ns).text or ""),
            "authors": authors,
            "published": (entry.find("atom:published", ns).text or "")[:10],
            "summary": (entry.find("atom:summary", ns).text or ""),
            "categories": categories,
        })
    return [format_arxiv_entry(r) for r in results]


async def get_crossref_by_doi(doi: str) -> dict:
    """通过 DOI 从 Crossref 获取单篇论文详情。"""
    async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
        resp = await client.get(f"{CROSSREF_API}/{doi}")
        resp.raise_for_status()
        return format_crossref_item(resp.json()["message"])


async def get_crossref_references(
    doi: str, limit: int = 20
) -> list[dict]:
    """获取某篇论文的参考文献列表。"""
    async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
        resp = await client.get(
            f"{CROSSREF_API}/{doi}",
            params={"select": "reference"},
        )
        resp.raise_for_status()
        refs = resp.json()["message"].get("reference", [])
        results = []
        for ref in refs[:limit]:
            results.append({
                "doi": ref.get("DOI", ""),
                "article_title": ref.get("article-title", ""),
                "journal_title": ref.get("journal-title", ""),
                "author": ref.get("author", ""),
                "year": ref.get("year", ""),
            })
        return results


# ---------- MCP 工具定义 ----------

@mcp.tool()
async def search_papers(query: str, limit: int = 10) -> str:
    """
    跨库搜索学术论文（同时搜 Crossref 和 arXiv）。

    Args:
        query: 搜索关键词，例如 "large language model retrieval augmented generation"
        limit: 每个数据库返回的最大结果数，默认 10
    """
    parts = [f"🔍 搜索: {query}\n"]

    # Crossref
    try:
        crossref_results = await search_crossref(query, limit)
        parts.append(f"\n📚 Crossref（{len(crossref_results)} 条）：")
        for i, r in enumerate(crossref_results, 1):
            parts.append(
                f"\n{i}. {r['title']}\n"
                f"   作者: {r['authors']}\n"
                f"   年份: {r['year']} | 期刊: {r['venue']}\n"
                f"   DOI: {r['doi']}\n"
                f"   被引: {r['cited_by']} 次\n"
                f"   摘要: {r['abstract'][:300]}"
            )
    except Exception as e:
        parts.append(f"\n⚠️ Crossref 搜索失败: {e}")

    # arXiv
    try:
        arxiv_results = await search_arxiv(query, limit)
        parts.append(f"\n\n📄 arXiv 预印本（{len(arxiv_results)} 条）：")
        for i, r in enumerate(arxiv_results, 1):
            parts.append(
                f"\n{i}. {r['title']}\n"
                f"   作者: {r['authors']}\n"
                f"   发布: {r['published']} | 分类: {r['categories']}\n"
                f"   arXiv: {r['arxiv_id']}\n"
                f"   摘要: {r['abstract'][:300]}"
            )
    except Exception as e:
        parts.append(f"\n⚠️ arXiv 搜索失败: {e}")

    return "\n".join(parts)


@mcp.tool()
async def get_paper(doi: str) -> str:
    """
    通过 DOI 获取单篇论文的详细信息（标题、作者、摘要、引用数等）。

    Args:
        doi: 论文的 DOI，例如 "10.1038/nature123456"
    """
    try:
        paper = await get_crossref_by_doi(doi)
        return (
            f"📄 {paper['title']}\n"
            f"作者: {paper['authors']}\n"
            f"年份: {paper['year']} | 期刊: {paper['venue']}\n"
            f"DOI: {paper['doi']}\n"
            f"URL: {paper['url']}\n"
            f"被引次数: {paper['cited_by']}\n\n"
            f"摘要:\n{paper['abstract']}"
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"未找到 DOI 为 {doi} 的论文。"
        return f"查询失败 (HTTP {e.response.status_code}): {e}"
    except Exception as e:
        return f"查询出错: {e}"


@mcp.tool()
async def get_references(doi: str, limit: int = 20) -> str:
    """
    获取某篇论文的参考文献列表。

    Args:
        doi: 论文的 DOI
        limit: 返回的参考文献最大数量，默认 20
    """
    try:
        refs = await get_crossref_references(doi, limit)
        if not refs:
            return "该论文没有可获取的参考文献数据（参考文献需要出版商注册了引用信息）。"
        lines = [f"📋 参考文献（{len(refs)} 条）：\n"]
        for i, ref in enumerate(refs, 1):
            title = ref["article_title"] or ref.get("journal_title", "（无标题）")
            author = ref["author"] or ""
            year = ref["year"] or ""
            doi_str = f"DOI: {ref['doi']}" if ref["doi"] else ""
            lines.append(f"{i}. {title} {author} {year} {doi_str}".strip())
        return "\n".join(lines)
    except Exception as e:
        return f"获取参考文献失败: {e}"


@mcp.tool()
async def search_arxiv_papers(query: str, limit: int = 10) -> str:
    """
    专门搜索 arXiv 预印本（计算机科学、物理、数学等领域最新研究）。

    Args:
        query: 搜索关键词
        limit: 返回结果数，默认 10
    """
    try:
        results = await search_arxiv(query, limit)
        if not results:
            return f"未找到与 '{query}' 相关的 arXiv 论文。"
        lines = [f"📄 arXiv 搜索结果（{len(results)} 条）：\n"]
        for i, r in enumerate(results, 1):
            lines.append(
                f"{i}. {r['title']}\n"
                f"   作者: {r['authors']}\n"
                f"   发布: {r['published']} | 分类: {r['categories']}\n"
                f"   arXiv ID: {r['arxiv_id']}\n"
                f"   摘要: {r['abstract'][:400]}\n"
            )
        return "\n".join(lines)
    except Exception as e:
        return f"arXiv 搜索失败: {e}"


# ---------- 启动 ----------

if __name__ == "__main__":
    mcp.run()
