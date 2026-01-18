"""Task 데이터 모델 정의."""

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Task 타입."""

    PROJECT = "Project"
    TASK = "Task"
    ISSUE = "Issue"
    EPIC = "Epic"


class TaskStatus(str, Enum):
    """Task 상태 (세부)."""

    # 할일 그룹 (to_do)
    ON_HOLD = "보류"
    NOT_STARTED = "시작 전"  # ✅ 띄어쓰기
    # 진행 중 그룹 (in_progress)
    IN_PROGRESS = "진행 중"  # ✅ 띄어쓰기
    # 완료 그룹 (complete)
    DONE = "완료"
    DEPLOYED = "배포됨"
    ARCHIVED = "보관"


class StatusGroup(str, Enum):
    """상태 그룹 - Notion 내부 값."""

    TODO = "to_do"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


# 상태 -> 그룹 매핑
STATUS_GROUP_MAP: dict[TaskStatus, StatusGroup] = {
    TaskStatus.ON_HOLD: StatusGroup.TODO,
    TaskStatus.NOT_STARTED: StatusGroup.TODO,
    TaskStatus.IN_PROGRESS: StatusGroup.IN_PROGRESS,
    TaskStatus.DONE: StatusGroup.COMPLETE,
    TaskStatus.DEPLOYED: StatusGroup.COMPLETE,
    TaskStatus.ARCHIVED: StatusGroup.COMPLETE,
}


class Priority(str, Enum):
    """우선순위."""

    LOW = "낮음"
    MEDIUM = "중간"
    HIGH = "높음"


class TaskLabel(str, Enum):
    """라벨 옵션."""

    MOBILE = "Mobile"
    WEB = "Web"
    PLANNING = "기획"
    DESIGN = "디자인"
    I18N = "다국어"
    BACKEND = "Backend"


class TaskService(str, Enum):
    """서비스 옵션."""

    ERP = "ERP"
    WIM_SERVICE = "WIM Service"
    SHOP = "자사몰"
    WIM_ADMIN = "WIM Admin"
    GLOBAL_HOMEPAGE = "글로벌홈페이지"


class Task(BaseModel):
    """Task 모델."""

    # 식별자
    id: str = Field(description="Notion 페이지 ID")
    url: str | None = Field(default=None, description="Notion 페이지 URL")
    task_no: int | None = Field(default=None, description="자동 생성 ID (ID 속성)")

    # 기본 속성
    title: str = Field(description="제목")
    task_type: TaskType | None = Field(default=None, description="타입")
    status: TaskStatus | None = Field(default=None, description="상태")
    priority: Priority | None = Field(default=None, description="우선순위")

    # 담당자/생성자
    assignee_id: str | None = Field(default=None, description="담당자 User ID")
    assignee_name: str | None = Field(default=None, description="담당자 이름")
    creator_id: str | None = Field(default=None, description="생성자 User ID")
    creator_name: str | None = Field(default=None, description="생성자 이름")

    # 분류
    labels: list[str] = Field(default_factory=list, description="라벨 목록")
    services: list[str] = Field(default_factory=list, description="서비스 목록")

    # 날짜
    start_date: date | None = Field(default=None, description="시작일")
    end_date: date | None = Field(default=None, description="종료일")
    done_date: datetime | None = Field(default=None, description="완료 일시 (Done)")

    # 계층 구조
    parent_id: str | None = Field(default=None, description="상위 항목 ID")
    children_ids: list[str] = Field(default_factory=list, description="하위 항목 ID 목록")

    # 시스템 속성 (읽기 전용)
    created_time: datetime | None = Field(default=None, description="생성 일시")
    last_edited_time: datetime | None = Field(default=None, description="최종 편집 일시")
    last_edited_by: str | None = Field(default=None, description="최종 편집자 ID")

    # Formula (읽기 전용)
    period: str | None = Field(default=None, description="Period (기간)")
    progress: float | None = Field(default=None, description="진행율")

    @property
    def status_group(self) -> StatusGroup | None:
        """상태 그룹 반환."""
        if self.status:
            return STATUS_GROUP_MAP.get(self.status)
        return None


class TaskCreate(BaseModel):
    """Task 생성 요청."""

    title: str = Field(description="제목")
    task_type: TaskType = Field(default=TaskType.TASK, description="타입")
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED, description="상태")
    priority: Priority | None = Field(default=None, description="우선순위")
    assignee_id: str | None = Field(default=None, description="담당자 User ID")
    start_date: date | None = Field(default=None, description="시작일")
    end_date: date | None = Field(default=None, description="종료일")
    labels: list[str] = Field(default_factory=list, description="라벨 목록")
    services: list[str] = Field(default_factory=list, description="서비스 목록")
    parent_id: str | None = Field(default=None, description="상위 항목 ID")


class TaskUpdate(BaseModel):
    """Task 수정 요청."""

    title: str | None = Field(default=None, description="제목")
    task_type: TaskType | None = Field(default=None, description="타입")
    status: TaskStatus | None = Field(default=None, description="상태")
    priority: Priority | None = Field(default=None, description="우선순위")
    assignee_id: str | None = Field(default=None, description="담당자 User ID")
    start_date: date | None = Field(default=None, description="시작일")
    end_date: date | None = Field(default=None, description="종료일")
    done_date: datetime | None = Field(default=None, description="완료 일시")
    labels: list[str] | None = Field(default=None, description="라벨 목록")
    services: list[str] | None = Field(default=None, description="서비스 목록")
    parent_id: str | None = Field(default=None, description="상위 항목 ID")


class TaskFilter(BaseModel):
    """Task 필터 조건."""

    task_type: TaskType | None = Field(default=None, description="타입 필터")
    status: TaskStatus | None = Field(default=None, description="상태 필터")
    status_group: StatusGroup | None = Field(default=None, description="상태 그룹 필터")
    priority: Priority | None = Field(default=None, description="우선순위 필터")
    assignee_id: str | None = Field(default=None, description="담당자 ID 필터")
    labels: list[str] | None = Field(default=None, description="라벨 필터 (OR 조건)")
    services: list[str] | None = Field(default=None, description="서비스 필터 (OR 조건)")
    start_date_from: date | None = Field(default=None, description="시작일 시작 범위")
    start_date_to: date | None = Field(default=None, description="시작일 종료 범위")
    end_date_from: date | None = Field(default=None, description="종료일 시작 범위")
    end_date_to: date | None = Field(default=None, description="종료일 종료 범위")
    parent_id: str | None = Field(default=None, description="상위 항목 ID 필터")
    has_parent: bool | None = Field(default=None, description="상위 항목 유무 필터")
