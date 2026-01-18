"""통합 테스트.

실제 Notion API를 사용하여 테스트합니다.
테스트 실행 전 .env 파일에 NOTION_API_KEY와 NOTION_DATABASE_ID를 설정해야 합니다.
"""

import os

import pytest
from dotenv import load_dotenv

from notion_task_mcp.models import Priority, TaskCreate, TaskStatus, TaskType, TaskUpdate
from notion_task_mcp.notion_client import NotionTaskClient


# 테스트 시작 전 환경변수 로드
load_dotenv()


@pytest.fixture
def client() -> NotionTaskClient:
    """Notion 클라이언트 fixture."""
    return NotionTaskClient()


@pytest.fixture
async def test_task(client: NotionTaskClient):
    """테스트용 Task 생성 및 정리."""
    # 테스트용 Task 생성
    task = await client.create_task(
        TaskCreate(
            title="[테스트] 통합 테스트용 Task",
            task_type=TaskType.TASK,
            status=TaskStatus.NOT_STARTED,
            priority=Priority.MEDIUM,
            labels=["테스트"],
        )
    )
    yield task
    # 테스트 후 삭제
    await client.delete_task(task.id)


@pytest.mark.skipif(
    not os.environ.get("NOTION_API_KEY"),
    reason="NOTION_API_KEY가 설정되지 않음",
)
class TestNotionTaskClient:
    """NotionTaskClient 통합 테스트."""

    async def test_list_tasks(self, client: NotionTaskClient):
        """Task 목록 조회 테스트."""
        tasks = await client.list_tasks(page_size=10)
        assert isinstance(tasks, list)

    async def test_create_and_get_task(self, client: NotionTaskClient):
        """Task 생성 및 조회 테스트."""
        # 생성
        task = await client.create_task(
            TaskCreate(
                title="[테스트] 생성 테스트",
                task_type=TaskType.TASK,
                status=TaskStatus.NOT_STARTED,
            )
        )
        assert task.id is not None
        assert task.title == "[테스트] 생성 테스트"

        # 조회
        fetched = await client.get_task(task.id)
        assert fetched.id == task.id
        assert fetched.title == task.title

        # 정리
        await client.delete_task(task.id)

    async def test_update_task(self, client: NotionTaskClient, test_task):
        """Task 수정 테스트."""
        updated = await client.update_task(
            test_task.id,
            TaskUpdate(
                title="[테스트] 수정된 제목",
                status=TaskStatus.IN_PROGRESS,
                priority=Priority.HIGH,
            ),
        )
        assert updated.title == "[테스트] 수정된 제목"
        assert updated.status == TaskStatus.IN_PROGRESS
        assert updated.priority == Priority.HIGH

    async def test_delete_task(self, client: NotionTaskClient):
        """Task 삭제 테스트."""
        # 삭제할 Task 생성
        task = await client.create_task(
            TaskCreate(title="[테스트] 삭제 테스트")
        )

        # 삭제
        result = await client.delete_task(task.id)
        assert result is True
