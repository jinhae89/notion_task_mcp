# Notion Task MCP - 프로젝트 개요

## 목적
Notion API를 활용한 Task 관리 MCP(Model Context Protocol) 서버.
AI 어시스턴트(Claude 등)가 Notion Task DB를 조회/관리할 수 있는 인터페이스 제공.

## 기술 스택
- **Language**: Python 3.11+
- **MCP SDK**: mcp >= 1.0.0
- **Notion SDK**: notion-client >= 2.0.0
- **Validation**: Pydantic >= 2.0.0
- **Env**: python-dotenv >= 1.0.0
- **Build**: hatchling

## 프로젝트 구조
```
src/notion_task_mcp/
├── __init__.py          # 패키지 초기화, 버전 정보
├── server.py            # MCP 서버 엔트리포인트 (create_server, run_server, main)
├── models.py            # Pydantic 데이터 모델
│   ├── TaskType         # Enum: Task, Epic, Issue, Project
│   ├── TaskStatus       # Enum: 보류, 시작전, 진행중, 완료, 배포됨, 보관
│   ├── StatusGroup      # Enum: 할일, 진행 중, 완료
│   ├── Priority         # Enum: 낮음, 중간, 높음
│   ├── Task             # 메인 Task 모델
│   ├── TaskCreate       # Task 생성 요청 모델
│   ├── TaskUpdate       # Task 수정 요청 모델
│   └── TaskFilter       # Task 필터 조건 모델
├── notion_client.py     # Notion API 비동기 클라이언트 래퍼
│   └── NotionTaskClient # CRUD, 필터, 일괄처리 메서드
└── tools/
    ├── __init__.py
    └── task_tools.py    # MCP Tool 정의 (7개 도구)
        ├── get_task
        ├── list_tasks
        ├── create_task
        ├── update_task
        ├── delete_task
        ├── batch_update_status
        └── batch_update_assignee

tests/
└── test_integration.py  # 통합 테스트 (실제 Notion API 사용)
```

## 환경 변수
MCP 클라이언트 설정(settings.json)에서 직접 지정:
- `NOTION_API_KEY`: Notion Integration Secret
- `NOTION_DATABASE_ID`: Task DB ID
