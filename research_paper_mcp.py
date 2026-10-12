"""
research-paper-mcp —— 命令行入口

这个模块的唯一作用是提供一个稳定的入口点，让 pip 安装后的命令
`research-paper-mcp` 以及 `python -m research_paper_mcp` 都能启动服务。

设计上刻意不改动 server.py：所有工具定义、API 调用逻辑仍然在 server.py 里。
这样做的好处是——如果你之后想重命名 server.py，只需要改这一个文件的 import。
"""

from server import mcp


def main() -> None:
    """启动 MCP 服务（stdio 传输）。"""
    mcp.run()


if __name__ == "__main__":
    main()
