"""Notion API 클라이언트 래퍼."""

import os
from datetime import date, datetime
from typing import Any

from notion_client import AsyncClient

from .models import (
    STATUS_GROUP_MAP,
    Priority,
    Task,
    TaskCreate,
    TaskFilter,
    TaskStatus,
    TaskType,
    TaskUpdate,
)


class NotionTaskClient:
    """Notion Task DB 클라이언트."""

    # Notion 속성명 매핑 (실제 DB 스키마 기준)
    PROP_ID = "ID"  # unique_id (기존 No → ID)
    PROP_TITLE = "제목"
    PROP_TYPE = "타입"
    PROP_STATUS = "상태"
    PROP_PRIORITY = "우선순위"
    PROP_ASSIGNEE = "담당자"
    PROP_CREATOR = "생성자"  # person 타입
    PROP_START_DATE = "시작일"
    PROP_END_DATE = "종료일"
    PROP_DONE = "Done"  # 완료 일시
    PROP_LABELS = "라벨"
    PROP_SERVICES = "서비스"
    PROP_PARENT = "상위 항목"  # ✅ 띄어쓰기
    PROP_CHILDREN = "하위 항목"  # ✅ 띄어쓰기
    PROP_PERIOD = "Period"  # ✅ 대문자
    PROP_PROGRESS = "진행율"
    PROP_CREATED_TIME = "생성 일시"
    PROP_LAST_EDITED_TIME = "최종 편집 일시"
    PROP_LAST_EDITED_BY = "최종 편집자"

    def __init__(
        self,
        api_key: str | None = None,
        database_id: str | None = None,
    ) -> None:
        """초기화.

        Args:
            api_key: Notion API 키. 없으면 환경변수에서 읽음.
            database_id: Notion 데이터베이스 ID. 없으면 환경변수에서 읽음.
        """
        self.api_key = api_key or os.environ.get("NOTION_API_KEY")
        self.database_id = database_id or os.environ.get("NOTION_DATABASE_ID")

        if not self.api_key:
            raise ValueError("NOTION_API_KEY가 필요합니다.")
        if not self.database_id:
            raise ValueError("NOTION_DATABASE_ID가 필요합니다.")

        self.client = AsyncClient(auth=self.api_key, notion_version="2025-09-03")
        self._data_source_id: str | None = None  # 캐시

    def _parse_task(self, page: dict[str, Any]) -> Task:
        """Notion 페이지를 Task 모델로 변환."""
        props = page["properties"]

        # ID (unique_id) 추출
        task_no = None
        if self.PROP_ID in props and props[self.PROP_ID].get("unique_id"):
            unique_id = props[self.PROP_ID]["unique_id"]
            task_no = unique_id.get("number")

        # 제목 추출
        title_prop = props.get(self.PROP_TITLE, {})
        title = ""
        if title_prop.get("title"):
            title = "".join(t["plain_text"] for t in title_prop["title"])

        # 타입 추출
        type_prop = props.get(self.PROP_TYPE, {})
        task_type = None
        if type_prop.get("select"):
            type_name = type_prop["select"]["name"]
            try:
                task_type = TaskType(type_name)
            except ValueError:
                pass

        # 상태 추출
        status_prop = props.get(self.PROP_STATUS, {})
        status = None
        if status_prop.get("status"):
            status_name = status_prop["status"]["name"]
            try:
                status = TaskStatus(status_name)
            except ValueError:
                pass

        # 우선순위 추출
        priority_prop = props.get(self.PROP_PRIORITY, {})
        priority = None
        if priority_prop.get("select"):
            priority_name = priority_prop["select"]["name"]
            try:
                priority = Priority(priority_name)
            except ValueError:
                pass

        # 담당자 추출 (person 타입)
        assignee_prop = props.get(self.PROP_ASSIGNEE, {})
        assignee_id = None
        assignee_name = None
        if assignee_prop.get("people") and len(assignee_prop["people"]) > 0:
            person = assignee_prop["people"][0]
            assignee_id = person.get("id")
            assignee_name = person.get("name")

        # 생성자 추출 (person 타입)
        creator_prop = props.get(self.PROP_CREATOR, {})
        creator_id = None
        creator_name = None
        if creator_prop.get("people") and len(creator_prop["people"]) > 0:
            person = creator_prop["people"][0]
            creator_id = person.get("id")
            creator_name = person.get("name")

        # 날짜 추출
        start_date = None
        start_date_prop = props.get(self.PROP_START_DATE, {})
        if start_date_prop.get("date"):
            start_str = start_date_prop["date"].get("start")
            if start_str:
                start_date = date.fromisoformat(start_str[:10])

        end_date = None
        end_date_prop = props.get(self.PROP_END_DATE, {})
        if end_date_prop.get("date"):
            end_str = end_date_prop["date"].get("start")
            if end_str:
                end_date = date.fromisoformat(end_str[:10])

        # Done (완료 일시) 추출
        done_date = None
        done_prop = props.get(self.PROP_DONE, {})
        if done_prop.get("date"):
            done_str = done_prop["date"].get("start")
            if done_str:
                done_date = datetime.fromisoformat(done_str.replace("Z", "+00:00"))

        # 라벨 추출
        labels_prop = props.get(self.PROP_LABELS, {})
        labels: list[str] = []
        if labels_prop.get("multi_select"):
            labels = [item["name"] for item in labels_prop["multi_select"]]

        # 서비스 추출
        services_prop = props.get(self.PROP_SERVICES, {})
        services: list[str] = []
        if services_prop.get("multi_select"):
            services = [item["name"] for item in services_prop["multi_select"]]

        # 상위 항목 추출 (⚠️ 띄어쓰기)
        parent_prop = props.get(self.PROP_PARENT, {})
        parent_id = None
        if parent_prop.get("relation") and len(parent_prop["relation"]) > 0:
            parent_id = parent_prop["relation"][0]["id"]

        # 하위 항목 추출 (⚠️ 띄어쓰기)
        children_prop = props.get(self.PROP_CHILDREN, {})
        children_ids: list[str] = []
        if children_prop.get("relation"):
            children_ids = [item["id"] for item in children_prop["relation"]]

        # 시스템 속성
        created_time = None
        if page.get("created_time"):
            created_time = datetime.fromisoformat(
                page["created_time"].replace("Z", "+00:00")
            )

        last_edited_time = None
        if page.get("last_edited_time"):
            last_edited_time = datetime.fromisoformat(
                page["last_edited_time"].replace("Z", "+00:00")
            )

        last_edited_by = None
        last_edited_by_prop = props.get(self.PROP_LAST_EDITED_BY, {})
        if last_edited_by_prop.get("last_edited_by"):
            last_edited_by = last_edited_by_prop["last_edited_by"].get("id")

        # Formula 속성 (Period, 진행율)
        period = None
        period_prop = props.get(self.PROP_PERIOD, {})
        if period_prop.get("formula"):
            formula = period_prop["formula"]
            if formula.get("string"):
                period = formula["string"]

        progress = None
        progress_prop = props.get(self.PROP_PROGRESS, {})
        if progress_prop.get("formula"):
            formula = progress_prop["formula"]
            if formula.get("number") is not None:
                progress = formula["number"]

        return Task(
            id=page["id"],
            url=page.get("url"),
            task_no=task_no,
            title=title,
            task_type=task_type,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            assignee_name=assignee_name,
            creator_id=creator_id,
            creator_name=creator_name,
            start_date=start_date,
            end_date=end_date,
            done_date=done_date,
            labels=labels,
            services=services,
            parent_id=parent_id,
            children_ids=children_ids,
            created_time=created_time,
            last_edited_time=last_edited_time,
            last_edited_by=last_edited_by,
            period=period,
            progress=progress,
        )

    def _build_properties(
        self,
        data: TaskCreate | TaskUpdate,
        is_update: bool = False,
    ) -> dict[str, Any]:
        """Task 데이터를 Notion 속성 형식으로 변환."""
        props: dict[str, Any] = {}

        # 제목
        if data.title is not None:
            props[self.PROP_TITLE] = {"title": [{"text": {"content": data.title}}]}

        # 타입
        if data.task_type is not None:
            props[self.PROP_TYPE] = {"select": {"name": data.task_type.value}}

        # 상태
        if data.status is not None:
            props[self.PROP_STATUS] = {"status": {"name": data.status.value}}

        # 우선순위
        if data.priority is not None:
            props[self.PROP_PRIORITY] = {"select": {"name": data.priority.value}}

        # 담당자
        if data.assignee_id is not None:
            props[self.PROP_ASSIGNEE] = {"people": [{"id": data.assignee_id}]}

        # 시작일
        if data.start_date is not None:
            props[self.PROP_START_DATE] = {"date": {"start": data.start_date.isoformat()}}
        elif is_update and hasattr(data, "start_date") and data.start_date is None:
            # 명시적으로 None 설정 시 제거
            props[self.PROP_START_DATE] = {"date": None}

        # 종료일
        if data.end_date is not None:
            props[self.PROP_END_DATE] = {"date": {"start": data.end_date.isoformat()}}
        elif is_update and hasattr(data, "end_date") and data.end_date is None:
            props[self.PROP_END_DATE] = {"date": None}

        # 완료 일시 (Done) - TaskUpdate에서만
        if isinstance(data, TaskUpdate) and data.done_date is not None:
            props[self.PROP_DONE] = {"date": {"start": data.done_date.isoformat()}}

        # 라벨
        if data.labels is not None:
            props[self.PROP_LABELS] = {
                "multi_select": [{"name": label} for label in data.labels]
            }

        # 서비스
        if data.services is not None:
            props[self.PROP_SERVICES] = {
                "multi_select": [{"name": service} for service in data.services]
            }

        # 상위 항목 (⚠️ 띄어쓰기)
        if data.parent_id is not None:
            props[self.PROP_PARENT] = {"relation": [{"id": data.parent_id}]}
        elif is_update and hasattr(data, "parent_id") and data.parent_id is None:
            props[self.PROP_PARENT] = {"relation": []}

        return props

    def _build_filter(self, filter_: TaskFilter) -> dict[str, Any] | None:
        """필터 조건을 Notion 필터 형식으로 변환."""
        conditions: list[dict[str, Any]] = []

        if filter_.task_type:
            conditions.append({
                "property": self.PROP_TYPE,
                "select": {"equals": filter_.task_type.value},
            })

        if filter_.status:
            conditions.append({
                "property": self.PROP_STATUS,
                "status": {"equals": filter_.status.value},
            })

        if filter_.status_group:
            # 그룹에 해당하는 모든 상태를 OR로 연결
            group_statuses = [
                s for s, g in STATUS_GROUP_MAP.items() if g == filter_.status_group
            ]
            status_conditions = [
                {"property": self.PROP_STATUS, "status": {"equals": s.value}}
                for s in group_statuses
            ]
            if len(status_conditions) > 1:
                conditions.append({"or": status_conditions})
            elif status_conditions:
                conditions.append(status_conditions[0])

        if filter_.priority:
            conditions.append({
                "property": self.PROP_PRIORITY,
                "select": {"equals": filter_.priority.value},
            })

        if filter_.assignee_id:
            conditions.append({
                "property": self.PROP_ASSIGNEE,
                "people": {"contains": filter_.assignee_id},
            })

        if filter_.labels:
            label_conditions = [
                {"property": self.PROP_LABELS, "multi_select": {"contains": label}}
                for label in filter_.labels
            ]
            if len(label_conditions) > 1:
                conditions.append({"or": label_conditions})
            elif label_conditions:
                conditions.append(label_conditions[0])

        if filter_.services:
            service_conditions = [
                {"property": self.PROP_SERVICES, "multi_select": {"contains": service}}
                for service in filter_.services
            ]
            if len(service_conditions) > 1:
                conditions.append({"or": service_conditions})
            elif service_conditions:
                conditions.append(service_conditions[0])

        if filter_.start_date_from:
            conditions.append({
                "property": self.PROP_START_DATE,
                "date": {"on_or_after": filter_.start_date_from.isoformat()},
            })

        if filter_.start_date_to:
            conditions.append({
                "property": self.PROP_START_DATE,
                "date": {"on_or_before": filter_.start_date_to.isoformat()},
            })

        if filter_.end_date_from:
            conditions.append({
                "property": self.PROP_END_DATE,
                "date": {"on_or_after": filter_.end_date_from.isoformat()},
            })

        if filter_.end_date_to:
            conditions.append({
                "property": self.PROP_END_DATE,
                "date": {"on_or_before": filter_.end_date_to.isoformat()},
            })

        if filter_.parent_id:
            conditions.append({
                "property": self.PROP_PARENT,
                "relation": {"contains": filter_.parent_id},
            })

        # 상위 항목 유무 필터
        if filter_.has_parent is True:
            conditions.append({
                "property": self.PROP_PARENT,
                "relation": {"is_not_empty": True},
            })
        elif filter_.has_parent is False:
            conditions.append({
                "property": self.PROP_PARENT,
                "relation": {"is_empty": True},
            })

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"and": conditions}

    async def get_task(self, task_id: str) -> Task:
        """Task 단건 조회.

        Args:
            task_id: Notion 페이지 ID.

        Returns:
            Task 모델.

        Raises:
            APIResponseError: Notion API 오류.
        """
        page = await self.client.pages.retrieve(page_id=task_id)
        return self._parse_task(page)

    async def list_tasks(
        self,
        filter_: TaskFilter | None = None,
        page_size: int = 100,
    ) -> list[Task]:
        """Task 목록 조회.

        Args:
            filter_: 필터 조건.
            page_size: 페이지 크기.

        Returns:
            Task 목록.
        """
        query_params: dict[str, Any] = {
            "database_id": self.database_id,
            "page_size": page_size,
        }

        if filter_:
            notion_filter = self._build_filter(filter_)
            if notion_filter:
                query_params["filter"] = notion_filter

        tasks = []
        has_more = True
        start_cursor = None

        # API 2025-09-03: data_source_id 사용
        data_source_id = await self._get_data_source_id()

        while has_more:
            if start_cursor:
                query_params["start_cursor"] = start_cursor

            response = await self.client.client.post(
                f"https://api.notion.com/v1/data_sources/{data_source_id}/query",
                json={k: v for k, v in query_params.items() if k != "database_id"},
            )
            response = response.json()
            for page in response["results"]:
                tasks.append(self._parse_task(page))

            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")

        return tasks

    async def create_task(self, data: TaskCreate) -> Task:
        """Task 생성.

        Args:
            data: 생성 데이터.

        Returns:
            생성된 Task.
        """
        properties = self._build_properties(data)

        # 템플릿 옵션 결정
        template: dict[str, Any] | None = None
        parent: dict[str, Any] = {"database_id": self.database_id}

        if data.template_id:
            template = {"type": "template_id", "template_id": data.template_id}
        elif data.use_default_template:
            # 기본 템플릿 사용 시 data_source_id로 parent 변경
            data_source_id = await self._get_data_source_id()
            template = {"type": "default"}
            parent = {"data_source_id": data_source_id}

        # 템플릿 사용 시 직접 HTTP 요청 (SDK가 template 파라미터 미지원)
        if template:
            request_body: dict[str, Any] = {
                "parent": parent,
                "properties": properties,
                "template": template,
            }
            response = await self.client.client.post(
                "https://api.notion.com/v1/pages",
                json=request_body,
            )
            page = response.json()
        else:
            page = await self.client.pages.create(
                parent=parent,
                properties=properties,
            )
        return self._parse_task(page)

    async def update_task(self, task_id: str, data: TaskUpdate) -> Task:
        """Task 수정.

        Args:
            task_id: Notion 페이지 ID.
            data: 수정 데이터.

        Returns:
            수정된 Task.
        """
        properties = self._build_properties(data, is_update=True)
        page = await self.client.pages.update(
            page_id=task_id,
            properties=properties,
        )
        return self._parse_task(page)

    async def delete_task(self, task_id: str) -> bool:
        """Task 삭제 (아카이브).

        Args:
            task_id: Notion 페이지 ID.

        Returns:
            성공 여부.
        """
        await self.client.pages.update(
            page_id=task_id,
            archived=True,
        )
        return True

    async def batch_update_status(
        self,
        task_ids: list[str],
        status: TaskStatus,
    ) -> list[Task]:
        """여러 Task 상태 일괄 변경.

        Args:
            task_ids: Notion 페이지 ID 목록.
            status: 변경할 상태.

        Returns:
            수정된 Task 목록.
        """
        updated_tasks = []
        for task_id in task_ids:
            task = await self.update_task(task_id, TaskUpdate(status=status))
            updated_tasks.append(task)
        return updated_tasks

    async def batch_update_assignee(
        self,
        task_ids: list[str],
        assignee_id: str,
    ) -> list[Task]:
        """여러 Task 담당자 일괄 변경.

        Args:
            task_ids: Notion 페이지 ID 목록.
            assignee_id: 담당자 User ID.

        Returns:
            수정된 Task 목록.
        """
        updated_tasks = []
        for task_id in task_ids:
            task = await self.update_task(task_id, TaskUpdate(assignee_id=assignee_id))
            updated_tasks.append(task)
        return updated_tasks

    async def _get_data_source_id(self) -> str:
        """Database에서 data_source_id를 조회 (캐시 사용).

        Returns:
            data_source_id.
        """
        if self._data_source_id:
            return self._data_source_id

        # Database 조회하여 data_sources 추출
        response = await self.client.client.get(
            f"https://api.notion.com/v1/databases/{self.database_id}",
        )
        db = response.json()

        data_sources = db.get("data_sources", [])
        if not data_sources:
            raise ValueError("Database에 data_source가 없습니다.")

        self._data_source_id = data_sources[0]["id"]
        return self._data_source_id

    async def list_templates(self) -> list[dict[str, Any]]:
        """사용 가능한 템플릿 목록 조회.

        Returns:
            템플릿 목록. 각 항목은 id, name, is_default 포함.
        """
        data_source_id = await self._get_data_source_id()

        response = await self.client.client.get(
            f"https://api.notion.com/v1/data_sources/{data_source_id}/templates",
        )
        data: dict[str, Any] = response.json()

        templates: list[dict[str, Any]] = data.get("templates", [])
        return templates

    async def get_template_by_type(self, task_type: str) -> dict[str, Any] | None:
        """타입명으로 템플릿 조회.

        Args:
            task_type: Task 타입 (Epic, Project, Issue, Task)

        Returns:
            매칭되는 템플릿 또는 None.
        """
        templates = await self.list_templates()
        for t in templates:
            # 템플릿 이름에 타입이 포함되어 있는지 확인
            if task_type.lower() in t["name"].lower():
                return t
        return None
