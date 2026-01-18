"""MCP 서버 엔트리포인트."""

import asyncio
import os

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .notion_client import NotionTaskClient
from .tools import register_task_tools


def create_server() -> Server:
    """MCP 서버 인스턴스 생성."""
    load_dotenv()

    server = Server("notion-task-mcp")

    # Notion 클라이언트 초기화
    notion_client = NotionTaskClient(
        api_key=os.environ.get("NOTION_API_KEY"),
        database_id=os.environ.get("NOTION_DATABASE_ID"),
    )

    # Task 도구 등록
    register_task_tools(server, notion_client)

    return server


async def run_server() -> None:
    """서버 실행."""
    server = create_server()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


def main() -> None:
    """메인 엔트리포인트."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
