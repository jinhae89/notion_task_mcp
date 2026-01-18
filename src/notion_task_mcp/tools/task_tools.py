"""Task 관련 MCP Tools."""

from datetime import date
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from ..models import (
    Priority,
    StatusGroup,
    TaskCreate,
    TaskFilter,
    TaskStatus,
    TaskType,
    TaskUpdate,
)
from ..notion_client import NotionTaskClient


def register_task_tools(server: Server, client: NotionTaskClient) -> None:
    """Task 관련 MCP 도구들을 서버에 등록."""

    @server.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
    async def list_tools() -> list[Tool]:
        """사용 가능한 도구 목록 반환."""
        return [
            Tool(
                name="get_task",
                description="Task 단건 조회. Notion 페이지 ID로 특정 Task의 상세 정보를 가져옵니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Notion 페이지 ID",
                        },
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="list_tasks",
                description="Task 목록 조회. 다양한 필터 조건으로 Task들을 검색합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_type": {
                            "type": "string",
                            "enum": ["Task", "Epic", "Issue", "Project"],
                            "description": "타입 필터",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["보류", "시작전", "진행중", "완료", "배포됨", "보관"],
                            "description": "상태 필터",
                        },
                        "status_group": {
                            "type": "string",
                            "enum": ["할일", "진행 중", "완료"],
                            "description": "상태 그룹 필터",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["낮음", "중간", "높음"],
                            "description": "우선순위 필터",
                        },
                        "assignee": {
                            "type": "string",
                            "description": "담당자 ID 필터",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "라벨 필터 (OR 조건)",
                        },
                        "services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "서비스 필터 (OR 조건)",
                        },
                        "start_date_from": {
                            "type": "string",
                            "format": "date",
                            "description": "시작일 시작 범위 (YYYY-MM-DD)",
                        },
                        "start_date_to": {
                            "type": "string",
                            "format": "date",
                            "description": "시작일 종료 범위 (YYYY-MM-DD)",
                        },
                        "end_date_from": {
                            "type": "string",
                            "format": "date",
                            "description": "종료일 시작 범위 (YYYY-MM-DD)",
                        },
                        "end_date_to": {
                            "type": "string",
                            "format": "date",
                            "description": "종료일 종료 범위 (YYYY-MM-DD)",
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "상위 항목 ID 필터",
                        },
                        "page_size": {
                            "type": "integer",
                            "description": "페이지 크기 (기본값: 100)",
                            "default": 100,
                        },
                    },
                },
            ),
            Tool(
                name="create_task",
                description="새 Task 생성.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "제목 (필수)",
                        },
                        "task_type": {
                            "type": "string",
                            "enum": ["Task", "Epic", "Issue", "Project"],
                            "description": "타입 (기본값: Task)",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["보류", "시작전", "진행중", "완료", "배포됨", "보관"],
                            "description": "상태 (기본값: 시작전)",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["낮음", "중간", "높음"],
                            "description": "우선순위",
                        },
                        "assignee": {
                            "type": "string",
                            "description": "담당자 ID",
                        },
                        "start_date": {
                            "type": "string",
                            "format": "date",
                            "description": "시작일 (YYYY-MM-DD)",
                        },
                        "end_date": {
                            "type": "string",
                            "format": "date",
                            "description": "종료일 (YYYY-MM-DD)",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "라벨 목록",
                        },
                        "services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "서비스 목록",
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "상위 항목 ID",
                        },
                    },
                    "required": ["title"],
                },
            ),
            Tool(
                name="update_task",
                description="기존 Task 수정.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Notion 페이지 ID (필수)",
                        },
                        "title": {
                            "type": "string",
                            "description": "제목",
                        },
                        "task_type": {
                            "type": "string",
                            "enum": ["Task", "Epic", "Issue", "Project"],
                            "description": "타입",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["보류", "시작전", "진행중", "완료", "배포됨", "보관"],
                            "description": "상태",
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["낮음", "중간", "높음"],
                            "description": "우선순위",
                        },
                        "assignee": {
                            "type": "string",
                            "description": "담당자 ID",
                        },
                        "start_date": {
                            "type": "string",
                            "format": "date",
                            "description": "시작일 (YYYY-MM-DD)",
                        },
                        "end_date": {
                            "type": "string",
                            "format": "date",
                            "description": "종료일 (YYYY-MM-DD)",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "라벨 목록",
                        },
                        "services": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "서비스 목록",
                        },
                        "parent_id": {
                            "type": "string",
                            "description": "상위 항목 ID",
                        },
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="delete_task",
                description="Task 삭제 (아카이브).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Notion 페이지 ID",
                        },
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="batch_update_status",
                description="여러 Task의 상태를 일괄 변경합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Notion 페이지 ID 목록",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["보류", "시작전", "진행중", "완료", "배포됨", "보관"],
                            "description": "변경할 상태",
                        },
                    },
                    "required": ["task_ids", "status"],
                },
            ),
            Tool(
                name="batch_update_assignee",
                description="여러 Task의 담당자를 일괄 변경합니다.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Notion 페이지 ID 목록",
                        },
                        "assignee": {
                            "type": "string",
                            "description": "담당자 ID",
                        },
                    },
                    "required": ["task_ids", "assignee"],
                },
            ),
        ]

    @server.call_tool()  # type: ignore[untyped-decorator]
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """도구 호출 처리."""

        def task_to_dict(task: Any) -> dict[str, Any]:
            """Task를 딕셔너리로 변환."""
            return {
                "id": task.id,
                "no": task.no,
                "title": task.title,
                "type": task.task_type.value,
                "status": task.status.value,
                "status_group": task.status_group.value,
                "priority": task.priority.value if task.priority else None,
                "assignee": task.assignee,
                "assignee_name": task.assignee_name,
                "creator": task.creator,
                "start_date": task.start_date.isoformat() if task.start_date else None,
                "end_date": task.end_date.isoformat() if task.end_date else None,
                "labels": task.labels,
                "services": task.services,
                "parent_id": task.parent_id,
                "children_ids": task.children_ids,
            }

        def parse_date(value: str | None) -> date | None:
            """날짜 문자열을 date 객체로 변환."""
            if value:
                return date.fromisoformat(value)
            return None

        import json

        try:
            if name == "get_task":
                task = await client.get_task(arguments["task_id"])
                result = task_to_dict(task)

            elif name == "list_tasks":
                filter_ = TaskFilter(
                    task_type=TaskType(arguments["task_type"]) if arguments.get("task_type") else None,
                    status=TaskStatus(arguments["status"]) if arguments.get("status") else None,
                    status_group=StatusGroup(arguments["status_group"]) if arguments.get("status_group") else None,
                    priority=Priority(arguments["priority"]) if arguments.get("priority") else None,
                    assignee=arguments.get("assignee"),
                    labels=arguments.get("labels"),
                    services=arguments.get("services"),
                    start_date_from=parse_date(arguments.get("start_date_from")),
                    start_date_to=parse_date(arguments.get("start_date_to")),
                    end_date_from=parse_date(arguments.get("end_date_from")),
                    end_date_to=parse_date(arguments.get("end_date_to")),
                    parent_id=arguments.get("parent_id"),
                )
                page_size = arguments.get("page_size", 100)
                tasks = await client.list_tasks(filter_=filter_, page_size=page_size)
                result = {"count": len(tasks), "tasks": [task_to_dict(t) for t in tasks]}

            elif name == "create_task":
                data = TaskCreate(
                    title=arguments["title"],
                    task_type=TaskType(arguments["task_type"]) if arguments.get("task_type") else TaskType.TASK,
                    status=TaskStatus(arguments["status"]) if arguments.get("status") else TaskStatus.NOT_STARTED,
                    priority=Priority(arguments["priority"]) if arguments.get("priority") else None,
                    assignee=arguments.get("assignee"),
                    start_date=parse_date(arguments.get("start_date")),
                    end_date=parse_date(arguments.get("end_date")),
                    labels=arguments.get("labels", []),
                    services=arguments.get("services", []),
                    parent_id=arguments.get("parent_id"),
                )
                task = await client.create_task(data)
                result = task_to_dict(task)

            elif name == "update_task":
                task_id = arguments.pop("task_id")
                update_data = TaskUpdate(
                    title=arguments.get("title"),
                    task_type=TaskType(arguments["task_type"]) if arguments.get("task_type") else None,
                    status=TaskStatus(arguments["status"]) if arguments.get("status") else None,
                    priority=Priority(arguments["priority"]) if arguments.get("priority") else None,
                    assignee=arguments.get("assignee"),
                    start_date=parse_date(arguments.get("start_date")),
                    end_date=parse_date(arguments.get("end_date")),
                    labels=arguments.get("labels"),
                    services=arguments.get("services"),
                    parent_id=arguments.get("parent_id"),
                )
                task = await client.update_task(task_id, update_data)
                result = task_to_dict(task)

            elif name == "delete_task":
                success = await client.delete_task(arguments["task_id"])
                result = {"success": success, "task_id": arguments["task_id"]}

            elif name == "batch_update_status":
                status = TaskStatus(arguments["status"])
                tasks = await client.batch_update_status(arguments["task_ids"], status)
                result = {"count": len(tasks), "tasks": [task_to_dict(t) for t in tasks]}

            elif name == "batch_update_assignee":
                tasks = await client.batch_update_assignee(
                    arguments["task_ids"],
                    arguments["assignee"],
                )
                result = {"count": len(tasks), "tasks": [task_to_dict(t) for t in tasks]}

            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]

            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]
