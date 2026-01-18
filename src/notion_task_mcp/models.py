"""Task 데이터 모델 정의."""

from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Task 타입."""

    TASK = "Task"
    EPIC = "Epic"
    ISSUE = "Issue"
    PROJECT = "Project"


class TaskStatus(str, Enum):
    """Task 상태 (세부)."""

    # 할일 그룹
    ON_HOLD = "보류"
    NOT_STARTED = "시작전"
    # 진행 중 그룹
    IN_PROGRESS = "진행중"
    # 완료 그룹
    DONE = "완료"
    DEPLOYED = "배포됨"
    ARCHIVED = "보관"


class StatusGroup(str, Enum):
    """상태 그룹."""

    TODO = "할일"
    IN_PROGRESS = "진행 중"
    DONE = "완료"


# 상태 -> 그룹 매핑
STATUS_GROUP_MAP: dict[TaskStatus, StatusGroup] = {
    TaskStatus.ON_HOLD: StatusGroup.TODO,
    TaskStatus.NOT_STARTED: StatusGroup.TODO,
    TaskStatus.IN_PROGRESS: StatusGroup.IN_PROGRESS,
    TaskStatus.DONE: StatusGroup.DONE,
    TaskStatus.DEPLOYED: StatusGroup.DONE,
    TaskStatus.ARCHIVED: StatusGroup.DONE,
}


class Priority(str, Enum):
    """우선순위."""

    LOW = "낮음"
    MEDIUM = "중간"
    HIGH = "높음"


class Task(BaseModel):
    """Task 모델."""

    id: str = Field(description="Notion 페이지 ID")
    no: str | None = Field(default=None, description="자동 생성 ID (Jira 티켓 ID와 같은 개념)")
    title: str = Field(description="제목")
    task_type: TaskType = Field(default=TaskType.TASK, description="타입")
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED, description="상태")
    priority: Priority | None = Field(default=None, description="우선순위")
    assignee: str | None = Field(default=None, description="담당자 ID")
    assignee_name: str | None = Field(default=None, description="담당자 이름")
    creator: str | None = Field(default=None, description="생성자 이름")
    start_date: date | None = Field(default=None, description="시작일")
    end_date: date | None = Field(default=None, description="종료일")
    labels: list[str] = Field(default_factory=list, description="라벨 목록")
    services: list[str] = Field(default_factory=list, description="서비스 목록")
    parent_id: str | None = Field(default=None, description="상위 항목 ID")
    children_ids: list[str] = Field(default_factory=list, description="하위 항목 ID 목록")

    @property
    def status_group(self) -> StatusGroup:
        """상태 그룹 반환."""
        return STATUS_GROUP_MAP[self.status]


class TaskCreate(BaseModel):
    """Task 생성 요청."""

    title: str = Field(description="제목")
    task_type: TaskType = Field(default=TaskType.TASK, description="타입")
    status: TaskStatus = Field(default=TaskStatus.NOT_STARTED, description="상태")
    priority: Priority | None = Field(default=None, description="우선순위")
    assignee: str | None = Field(default=None, description="담당자 ID")
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
    assignee: str | None = Field(default=None, description="담당자 ID")
    start_date: date | None = Field(default=None, description="시작일")
    end_date: date | None = Field(default=None, description="종료일")
    labels: list[str] | None = Field(default=None, description="라벨 목록")
    services: list[str] | None = Field(default=None, description="서비스 목록")
    parent_id: str | None = Field(default=None, description="상위 항목 ID")


class TaskFilter(BaseModel):
    """Task 필터 조건."""

    task_type: TaskType | None = Field(default=None, description="타입 필터")
    status: TaskStatus | None = Field(default=None, description="상태 필터")
    status_group: StatusGroup | None = Field(default=None, description="상태 그룹 필터")
    priority: Priority | None = Field(default=None, description="우선순위 필터")
    assignee: str | None = Field(default=None, description="담당자 ID 필터")
    labels: list[str] | None = Field(default=None, description="라벨 필터 (OR 조건)")
    services: list[str] | None = Field(default=None, description="서비스 필터 (OR 조건)")
    start_date_from: date | None = Field(default=None, description="시작일 시작 범위")
    start_date_to: date | None = Field(default=None, description="시작일 종료 범위")
    end_date_from: date | None = Field(default=None, description="종료일 시작 범위")
    end_date_to: date | None = Field(default=None, description="종료일 종료 범위")
    parent_id: str | None = Field(default=None, description="상위 항목 ID 필터")
