#!/usr/bin/env python3
"""Notion Task CLI - Claude Skills용 CLI 스크립트.

사용법:
    python3 notion_task_cli.py list [--status STATUS] [--priority PRIORITY]
    python3 notion_task_cli.py get <task_id>
    python3 notion_task_cli.py create --title TITLE [--type TYPE] [--priority PRIORITY]
    python3 notion_task_cli.py update <task_id> [--status STATUS] [--priority PRIORITY]
    python3 notion_task_cli.py done <task_id>

환경변수:
    NOTION_API_KEY: Notion API 키
    NOTION_DATABASE_ID: Notion 데이터베이스 ID
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import ssl


# ============== Config 로딩 ==============

def load_config() -> dict[str, Any]:
    """config.json 파일 로드."""
    config_path = Path(__file__).parent.parent / "config.json"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


CONFIG = load_config()

# SSL 컨텍스트 설정 (macOS 인증서 문제 해결)
try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()
    SSL_CONTEXT.check_hostname = False
    SSL_CONTEXT.verify_mode = ssl.CERT_NONE


# ============== Notion API 클라이언트 ==============

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


class NotionTaskClient:
    """Notion Task DB 클라이언트."""

    PROP_TITLE = "제목"
    PROP_TYPE = "타입"
    PROP_STATUS = "상태"
    PROP_PRIORITY = "우선순위"
    PROP_ASSIGNEE = "담당자"
    PROP_LABELS = "라벨"
    PROP_SERVICES = "서비스"
    PROP_START_DATE = "시작일"
    PROP_END_DATE = "종료일"
    PROP_PARENT = "상위 항목"
    PROP_CHILDREN = "하위 항목"

    def __init__(self):
        # config.json > 환경변수 순서로 값 획득
        self.api_key = CONFIG.get("notion", {}).get("api_key") or os.environ.get("NOTION_API_KEY")
        self.database_id = CONFIG.get("notion", {}).get("database_id") or os.environ.get("NOTION_DATABASE_ID")

        if not self.api_key:
            raise ValueError("Notion API Key가 필요합니다. (config.json 또는 NOTION_API_KEY 환경변수)")
        if not self.database_id:
            raise ValueError("Notion Database ID가 필요합니다. (config.json 또는 NOTION_DATABASE_ID 환경변수)")

    def _request(self, method: str, endpoint: str, body: dict | None = None) -> dict:
        """Notion API 요청."""
        url = f"{NOTION_API_BASE}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }

        data = json.dumps(body).encode("utf-8") if body else None
        req = Request(url, data=data, headers=headers, method=method)

        try:
            with urlopen(req, context=SSL_CONTEXT) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise Exception(f"Notion API Error: {e.code} - {error_body}")

    def _parse_task(self, page: dict[str, Any]) -> dict[str, Any]:
        """Notion 페이지를 딕셔너리로 변환."""
        props = page["properties"]

        # 제목
        title = ""
        if props.get(self.PROP_TITLE, {}).get("title"):
            title = "".join(t["plain_text"] for t in props[self.PROP_TITLE]["title"])

        # 타입
        task_type = "Task"
        if props.get(self.PROP_TYPE, {}).get("select"):
            task_type = props[self.PROP_TYPE]["select"]["name"]

        # 상태
        status = "시작 전"
        if props.get(self.PROP_STATUS, {}).get("status"):
            status = props[self.PROP_STATUS]["status"]["name"]

        # 우선순위
        priority = None
        if props.get(self.PROP_PRIORITY, {}).get("select"):
            priority = props[self.PROP_PRIORITY]["select"]["name"]

        # 담당자
        assignee = None
        if props.get(self.PROP_ASSIGNEE, {}).get("people"):
            people = props[self.PROP_ASSIGNEE]["people"]
            if people:
                assignee = people[0].get("name")

        # 라벨
        labels = []
        if props.get(self.PROP_LABELS, {}).get("multi_select"):
            labels = [item["name"] for item in props[self.PROP_LABELS]["multi_select"]]

        # 서비스
        services = []
        if props.get(self.PROP_SERVICES, {}).get("multi_select"):
            services = [item["name"] for item in props[self.PROP_SERVICES]["multi_select"]]

        # No (unique_id)
        no = None
        if "ID" in props and props["ID"].get("unique_id"):
            unique_id = props["ID"]["unique_id"]
            prefix = unique_id.get("prefix", "")
            number = unique_id.get("number", "")
            no = f"{prefix}-{number}" if prefix else str(number)

        # 시작일
        start_date = None
        if props.get(self.PROP_START_DATE, {}).get("date"):
            start_date = props[self.PROP_START_DATE]["date"].get("start")

        # 종료일
        end_date = None
        if props.get(self.PROP_END_DATE, {}).get("date"):
            end_date = props[self.PROP_END_DATE]["date"].get("start")

        # 상위 항목 (parent relations)
        parent_ids = []
        if props.get(self.PROP_PARENT, {}).get("relation"):
            parent_ids = [r["id"] for r in props[self.PROP_PARENT]["relation"]]

        # 하위 항목 (children relations)
        children_ids = []
        if props.get(self.PROP_CHILDREN, {}).get("relation"):
            children_ids = [r["id"] for r in props[self.PROP_CHILDREN]["relation"]]

        return {
            "id": page["id"],
            "no": no,
            "title": title,
            "type": task_type,
            "status": status,
            "priority": priority,
            "assignee": assignee,
            "start_date": start_date,
            "end_date": end_date,
            "parent_ids": parent_ids,
            "children_ids": children_ids,
            "labels": labels,
            "services": services,
            "url": page.get("url"),
        }

    def list_tasks(
        self,
        status: str | None = None,
        priority: str | None = None,
        assignee: str | None = None,
        task_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Task 목록 조회."""
        conditions = []

        if status:
            conditions.append({
                "property": self.PROP_STATUS,
                "status": {"equals": status},
            })

        if priority:
            conditions.append({
                "property": self.PROP_PRIORITY,
                "select": {"equals": priority},
            })

        if assignee:
            conditions.append({
                "property": self.PROP_ASSIGNEE,
                "people": {"contains": assignee},
            })

        if task_type:
            conditions.append({
                "property": self.PROP_TYPE,
                "select": {"equals": task_type},
            })

        body: dict[str, Any] = {}
        if conditions:
            if len(conditions) == 1:
                body["filter"] = conditions[0]
            else:
                body["filter"] = {"and": conditions}

        tasks = []
        has_more = True
        start_cursor = None

        while has_more:
            if start_cursor:
                body["start_cursor"] = start_cursor

            response = self._request("POST", f"databases/{self.database_id}/query", body)
            for page in response["results"]:
                tasks.append(self._parse_task(page))

            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return tasks

    def get_task(self, task_id: str) -> dict[str, Any]:
        """Task 단건 조회."""
        response = self._request("GET", f"pages/{task_id}")
        return self._parse_task(response)

    def create_task(
        self,
        title: str,
        task_type: str = "Task",
        status: str = "시작 전",
        priority: str | None = None,
        labels: list[str] | None = None,
        services: list[str] | None = None,
        assignee: str | None = None,
    ) -> dict[str, Any]:
        """Task 생성.

        Args:
            assignee: Notion 사용자 ID (UUID 형식)
        """
        properties: dict[str, Any] = {
            self.PROP_TITLE: {"title": [{"text": {"content": title}}]},
            self.PROP_TYPE: {"select": {"name": task_type}},
            self.PROP_STATUS: {"status": {"name": status}},
        }

        if priority:
            properties[self.PROP_PRIORITY] = {"select": {"name": priority}}

        if labels:
            properties[self.PROP_LABELS] = {
                "multi_select": [{"name": label} for label in labels]
            }

        if services:
            properties[self.PROP_SERVICES] = {
                "multi_select": [{"name": service} for service in services]
            }

        if assignee:
            properties[self.PROP_ASSIGNEE] = {
                "people": [{"id": assignee}]
            }

        body = {
            "parent": {"database_id": self.database_id},
            "properties": properties,
        }

        response = self._request("POST", "pages", body)
        return self._parse_task(response)

    def update_task(
        self,
        task_id: str,
        title: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any]:
        """Task 수정.

        Args:
            start_date: 시작일 (YYYY-MM-DD 형식)
            end_date: 종료일 (YYYY-MM-DD 형식)
        """
        properties: dict[str, Any] = {}

        if title:
            properties[self.PROP_TITLE] = {"title": [{"text": {"content": title}}]}

        if status:
            properties[self.PROP_STATUS] = {"status": {"name": status}}

        if priority:
            properties[self.PROP_PRIORITY] = {"select": {"name": priority}}

        if start_date:
            properties[self.PROP_START_DATE] = {"date": {"start": start_date}}

        if end_date:
            properties[self.PROP_END_DATE] = {"date": {"start": end_date}}

        body = {"properties": properties}
        response = self._request("PATCH", f"pages/{task_id}", body)
        return self._parse_task(response)

    def complete_task(self, task_id: str) -> dict[str, Any]:
        """Task 완료 처리."""
        return self.update_task(task_id, status="완료")

    def get_related_items(self, task_ids: list[str]) -> list[dict[str, Any]]:
        """여러 Task ID로 상세 정보 조회."""
        items = []
        for task_id in task_ids:
            try:
                item = self.get_task(task_id)
                items.append(item)
            except Exception:
                pass
        return items

    def get_my_projects(self, assignee_id: str | None = None) -> list[dict[str, Any]]:
        """내가 담당자인 Project 목록 또는 내 Task의 상위 Project 목록."""
        # 방법 1: 직접 담당자인 Project
        projects = self.list_tasks(task_type="Project", assignee=assignee_id)

        # 방법 2: 내 Task들의 상위 Project 찾기
        my_tasks = self.list_tasks(task_type="Task", assignee=assignee_id)
        parent_ids = set()
        for task in my_tasks:
            parent_ids.update(task.get("parent_ids", []))

        if parent_ids:
            parent_items = self.get_related_items(list(parent_ids))
            # Project 타입만 필터링
            for item in parent_items:
                if item.get("type") == "Project" and item["id"] not in [p["id"] for p in projects]:
                    projects.append(item)

        return projects

    def get_my_epics(self, assignee_id: str | None = None) -> list[dict[str, Any]]:
        """내가 담당자인 Epic 목록 또는 내 Task의 상위 Epic 목록."""
        # 방법 1: 직접 담당자인 Epic
        epics = self.list_tasks(task_type="Epic", assignee=assignee_id)

        # 방법 2: 내 Task들의 상위 Epic 찾기
        my_tasks = self.list_tasks(task_type="Task", assignee=assignee_id)
        parent_ids = set()
        for task in my_tasks:
            parent_ids.update(task.get("parent_ids", []))

        if parent_ids:
            parent_items = self.get_related_items(list(parent_ids))
            # Epic 타입만 필터링
            for item in parent_items:
                if item.get("type") == "Epic" and item["id"] not in [e["id"] for e in epics]:
                    epics.append(item)

        return epics


# ============== CLI 함수 ==============

def format_task(task: dict[str, Any], verbose: bool = False) -> str:
    """Task를 문자열로 포맷."""
    priority_emoji = {"높음": "🔴", "중간": "🟡", "낮음": "🟢"}.get(task.get("priority") or "", "⚪")
    status_emoji = {
        "진행 중": "🔄",
        "완료": "✅",
        "시작 전": "📋",
        "보류": "⏸️",
        "배포됨": "🚀",
        "보관": "📦",
    }.get(task.get("status") or "", "❓")

    line = f"{status_emoji} [{task.get('no') or task['id'][:8]}] {task['title']}"

    if task.get("priority"):
        line += f" {priority_emoji}"

    if task.get("assignee"):
        line += f" (@{task['assignee']})"

    if verbose:
        if task.get("labels"):
            line += f"\n   라벨: {', '.join(task['labels'])}"
        if task.get("services"):
            line += f"\n   서비스: {', '.join(task['services'])}"
        if task.get("url"):
            line += f"\n   URL: {task['url']}"

    return line


def format_tasks_table(tasks: list[dict[str, Any]]) -> str:
    """Task 목록을 테이블 형식으로 포맷."""
    if not tasks:
        return "조회된 Task가 없습니다."

    lines = []
    lines.append(f"총 {len(tasks)}개의 Task")
    lines.append("-" * 60)

    for task in tasks:
        lines.append(format_task(task))

    return "\n".join(lines)


def cmd_list(args: argparse.Namespace) -> None:
    """list 명령어 처리."""
    client = NotionTaskClient()
    tasks = client.list_tasks(
        status=args.status,
        priority=args.priority,
        assignee=args.assignee,
        task_type=args.type,
    )

    if args.json:
        print(json.dumps(tasks, ensure_ascii=False, indent=2, default=str))
    else:
        print(format_tasks_table(tasks))


def cmd_get(args: argparse.Namespace) -> None:
    """get 명령어 처리."""
    client = NotionTaskClient()
    task = client.get_task(args.task_id)

    if args.json:
        print(json.dumps(task, ensure_ascii=False, indent=2, default=str))
    else:
        print(format_task(task, verbose=True))


def cmd_create(args: argparse.Namespace) -> None:
    """create 명령어 처리."""
    client = NotionTaskClient()

    # 담당자 결정: CLI 인자 > config 자동 지정
    assignee = args.assignee
    if not assignee and CONFIG.get("defaults", {}).get("auto_assign"):
        assignee = CONFIG.get("user", {}).get("notion_id")

    # 우선순위: CLI 인자 > config 기본값
    priority = args.priority
    if not priority and CONFIG.get("defaults", {}).get("priority"):
        priority = CONFIG["defaults"]["priority"]

    task = client.create_task(
        title=args.title,
        task_type=args.type or CONFIG.get("defaults", {}).get("type", "Task"),
        priority=priority,
        labels=args.labels.split(",") if args.labels else None,
        services=args.services.split(",") if args.services else None,
        assignee=assignee,
    )

    if args.json:
        print(json.dumps(task, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"✅ Task 생성 완료: {format_task(task)}")


def cmd_update(args: argparse.Namespace) -> None:
    """update 명령어 처리."""
    client = NotionTaskClient()
    task = client.update_task(
        task_id=args.task_id,
        title=args.title,
        status=args.status,
        priority=args.priority,
        start_date=args.start_date,
        end_date=args.end_date,
    )

    if args.json:
        print(json.dumps(task, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"✅ Task 수정 완료: {format_task(task)}")


def cmd_done(args: argparse.Namespace) -> None:
    """done 명령어 처리."""
    client = NotionTaskClient()
    task = client.complete_task(args.task_id)

    if args.json:
        print(json.dumps(task, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"✅ Task 완료 처리: {format_task(task)}")


def cmd_projects(args: argparse.Namespace) -> None:
    """projects 명령어 처리 - 내 Project 목록."""
    client = NotionTaskClient()
    assignee_id = args.assignee or CONFIG.get("user", {}).get("notion_id")
    projects = client.get_my_projects(assignee_id)

    if args.json:
        print(json.dumps(projects, ensure_ascii=False, indent=2, default=str))
    else:
        if not projects:
            print("연관된 Project가 없습니다.")
        else:
            print(f"📁 내 Project 목록 ({len(projects)}개)")
            print("-" * 60)
            for p in projects:
                print(format_task(p))


def cmd_epics(args: argparse.Namespace) -> None:
    """epics 명령어 처리 - 내 Epic 목록."""
    client = NotionTaskClient()
    assignee_id = args.assignee or CONFIG.get("user", {}).get("notion_id")
    epics = client.get_my_epics(assignee_id)

    if args.json:
        print(json.dumps(epics, ensure_ascii=False, indent=2, default=str))
    else:
        if not epics:
            print("연관된 Epic이 없습니다.")
        else:
            print(f"🎯 내 Epic 목록 ({len(epics)}개)")
            print("-" * 60)
            for e in epics:
                print(format_task(e))


# ============== 메인 ==============

def main():
    parser = argparse.ArgumentParser(
        description="Notion Task CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--json", action="store_true", help="JSON 형식으로 출력")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list
    list_parser = subparsers.add_parser("list", help="Task 목록 조회")
    list_parser.add_argument("--status", help="상태 필터 (진행 중, 완료, 시작 전, 보류)")
    list_parser.add_argument("--priority", help="우선순위 필터 (높음, 중간, 낮음)")
    list_parser.add_argument("--assignee", help="담당자 ID 필터")
    list_parser.add_argument("--type", help="타입 필터 (Task, Epic, Issue, Project)")
    list_parser.set_defaults(func=cmd_list)

    # get
    get_parser = subparsers.add_parser("get", help="Task 단건 조회")
    get_parser.add_argument("task_id", help="Task ID")
    get_parser.set_defaults(func=cmd_get)

    # create
    create_parser = subparsers.add_parser("create", help="Task 생성")
    create_parser.add_argument("--title", required=True, help="제목")
    create_parser.add_argument("--type", help="타입 (Task, Epic, Issue, Project)")
    create_parser.add_argument("--priority", help="우선순위 (높음, 중간, 낮음)")
    create_parser.add_argument("--labels", help="라벨 (쉼표로 구분)")
    create_parser.add_argument("--services", help="서비스 (쉼표로 구분)")
    create_parser.add_argument("--assignee", help="담당자 Notion ID (미지정시 config에서 자동 지정)")
    create_parser.set_defaults(func=cmd_create)

    # update
    update_parser = subparsers.add_parser("update", help="Task 수정")
    update_parser.add_argument("task_id", help="Task ID")
    update_parser.add_argument("--title", help="제목")
    update_parser.add_argument("--status", help="상태")
    update_parser.add_argument("--priority", help="우선순위")
    update_parser.add_argument("--start-date", dest="start_date", help="시작일 (YYYY-MM-DD)")
    update_parser.add_argument("--end-date", dest="end_date", help="종료일 (YYYY-MM-DD)")
    update_parser.set_defaults(func=cmd_update)

    # done
    done_parser = subparsers.add_parser("done", help="Task 완료 처리")
    done_parser.add_argument("task_id", help="Task ID")
    done_parser.set_defaults(func=cmd_done)

    # projects
    projects_parser = subparsers.add_parser("projects", help="내 Project 목록")
    projects_parser.add_argument("--assignee", help="담당자 ID (미지정시 config에서 자동)")
    projects_parser.set_defaults(func=cmd_projects)

    # epics
    epics_parser = subparsers.add_parser("epics", help="내 Epic 목록")
    epics_parser.add_argument("--assignee", help="담당자 ID (미지정시 config에서 자동)")
    epics_parser.set_defaults(func=cmd_epics)

    args = parser.parse_args()

    try:
        args.func(args)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
