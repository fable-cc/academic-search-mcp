"""
Academic Search Web UI - 浏览器版学术论文搜索
直接运行：python web.py
然后打开 http://localhost:8000
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from server import search_crossref, search_arxiv

app = FastAPI(title="Academic Search")


@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Academic Search - 学术论文搜索</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: #f5f5f7;
    min-height: 100vh;
    padding: 40px 20px;
  }
  .container { max-width: 800px; margin: 0 auto; }
  h1 {
    font-size: 28px;
    font-weight: 700;
    color: #1d1d1f;
    margin-bottom: 8px;
  }
  .subtitle {
    color: #86868b;
    font-size: 15px;
    margin-bottom: 32px;
  }
  .search-box {
    display: flex;
    gap: 8px;
    margin-bottom: 32px;
  }
  .search-box input {
    flex: 1;
    padding: 14px 20px;
    border: 2px solid #d2d2d7;
    border-radius: 12px;
    font-size: 16px;
    outline: none;
    transition: border-color 0.2s;
  }
  .search-box input:focus { border-color: #0071e3; }
  .search-box button {
    padding: 14px 28px;
    background: #0071e3;
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
  }
  .search-box button:hover { background: #0077ed; }
  .search-box button:disabled { background: #999; cursor: not-allowed; }
  .source-label {
    font-size: 13px;
    font-weight: 600;
    color: #86868b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 24px 0 12px;
  }
  .paper-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  }
  .paper-card h3 {
    font-size: 16px;
    font-weight: 600;
    color: #1d1d1f;
    margin-bottom: 6px;
    line-height: 1.4;
  }
  .paper-meta {
    font-size: 13px;
    color: #86868b;
    margin-bottom: 8px;
  }
  .paper-meta span { margin-right: 12px; }
  .paper-abstract {
    font-size: 14px;
    color: #424245;
    line-height: 1.5;
    margin-top: 8px;
  }
  .paper-doi {
    font-size: 13px;
    margin-top: 10px;
  }
  .paper-doi a {
    color: #0071e3;
    text-decoration: none;
  }
  .paper-doi a:hover { text-decoration: underline; }
  .loading {
    text-align: center;
    padding: 40px;
    color: #86868b;
    font-size: 15px;
  }
  .error {
    background: #fff2f2;
    color: #d70015;
    padding: 16px;
    border-radius: 12px;
    font-size: 14px;
  }
  .empty {
    text-align: center;
    padding: 60px 20px;
    color: #86868b;
  }
  .empty-icon { font-size: 48px; margin-bottom: 16px; }
</style>
</head>
<body>
<div class="container">
  <h1>Academic Search</h1>
  <p class="subtitle">搜索 Crossref（1.87 亿篇论文）+ arXiv（290 万篇预印本）</p>

  <div class="search-box">
    <input type="text" id="query" placeholder="输入关键词，如 retrieval augmented generation" autofocus>
    <button onclick="doSearch()" id="searchBtn">搜索</button>
  </div>

  <div id="results"></div>
</div>

<script>
document.getElementById('query').addEventListener('keypress', function(e) {
  if (e.key === 'Enter') doSearch();
});

async function doSearch() {
  const q = document.getElementById('query').value.trim();
  if (!q) return;

  const btn = document.getElementById('searchBtn');
  btn.disabled = true;
  btn.textContent = '搜索中...';
  document.getElementById('results').innerHTML = '<div class="loading">正在搜索学术数据库...</div>';

  try {
    const resp = await fetch('/api/search?q=' + encodeURIComponent(q));
    const data = await resp.json();

    let html = '';

    if (data.crossref && data.crossref.length > 0) {
      html += '<div class="source-label">📚 Crossref（期刊论文）</div>';
      data.crossref.forEach((p, i) => {
        html += `<div class="paper-card">
          <h3>${i+1}. ${p.title}</h3>
          <div class="paper-meta">
            <span>👤 ${p.authors}</span>
            ${p.year ? `<span>📅 ${p.year}</span>` : ''}
            ${p.cited_by ? `<span>📊 被引 ${p.cited_by} 次</span>` : ''}
          </div>
          ${p.abstract && p.abstract !== '（无摘要）' ? `<div class="paper-abstract">${p.abstract.substring(0, 400)}${p.abstract.length > 400 ? '...' : ''}</div>` : ''}
          ${p.doi ? `<div class="paper-doi"><a href="https://doi.org/${p.doi}" target="_blank">DOI: ${p.doi}</a></div>` : ''}
        </div>`;
      });
    }

    if (data.arxiv && data.arxiv.length > 0) {
      html += '<div class="source-label">📄 arXiv（预印本）</div>';
      data.arxiv.forEach((p, i) => {
        html += `<div class="paper-card">
          <h3>${i+1}. ${p.title}</h3>
          <div class="paper-meta">
            <span>👤 ${p.authors}</span>
            <span>📅 ${p.published}</span>
            ${p.categories ? `<span>🏷 ${p.categories}</span>` : ''}
          </div>
          ${p.abstract ? `<div class="paper-abstract">${p.abstract.substring(0, 400)}${p.abstract.length > 400 ? '...' : ''}</div>` : ''}
          <div class="paper-doi"><a href="https://arxiv.org/abs/${p.arxiv_id}" target="_blank">arXiv: ${p.arxiv_id}</a></div>
        </div>`;
      });
    }

    if (!html) {
      html = '<div class="empty"><div class="empty-icon">🔍</div>没有找到相关论文</div>';
    }

    document.getElementById('results').innerHTML = html;
  } catch (e) {
    document.getElementById('results').innerHTML = '<div class="error">搜索失败: ' + e.message + '</div>';
  } finally {
    btn.disabled = false;
    btn.textContent = '搜索';
  }
}
</script>
</body>
</html>
"""


@app.get("/api/search")
async def search(q: str):
    """搜索 API：同时查 Crossref 和 arXiv"""
    crossref_results = await search_crossref(q, limit=8)
    arxiv_results = await search_arxiv(q, limit=8)
    return {
        "crossref": crossref_results,
        "arxiv": arxiv_results,
    }


if __name__ == "__main__":
    print("启动 Academic Search Web UI...")
    print("打开浏览器访问: http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
