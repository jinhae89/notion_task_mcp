# Project Context

## Purpose
Notion API를 활용한 Task 관리 MCP(Model Context Protocol) 서버.
Jira와 유사한 티켓 기반 일감 관리 시스템을 Notion DB로 구현하고, AI 어시스턴트가 이를 조회/관리할 수 있도록 MCP 인터페이스를 제공한다.

## Tech Stack
- **Language**: Python 3.11+
- **MCP SDK**: mcp (공식 Python SDK)
- **Notion Client**: notion-client (공식 Python SDK)
- **패키지 관리**: uv 또는 pip
- **타입 체크**: mypy (권장)

## Project Conventions

### Code Style
- PEP 8 준수
- 타입 힌트 적극 활용
- Docstring: Google style
- 변수/함수명: snake_case
- 클래스명: PascalCase
- 상수: UPPER_SNAKE_CASE

### Architecture Patterns
- **구조**: 단일 MCP 서버 모듈
- **계층 분리**:
  - `server.py`: MCP 서버 엔트리포인트
  - `notion_client.py`: Notion API 래퍼
  - `models.py`: Task 데이터 모델 (Pydantic)
  - `tools/`: MCP Tool 정의

### Module Details

#### models.py
데이터 모델 정의 (모두 Pydantic BaseModel 또는 Enum):
- `TaskType`: Task, Epic, Issue, Project
- `TaskStatus`: 보류, 시작전, 진행중, 완료, 배포됨, 보관
- `StatusGroup`: 할일, 진행 중, 완료
- `Priority`: 낮음, 중간, 높음
- `STATUS_GROUP_MAP`: 상태 → 그룹 매핑 상수
- `Task`: 메인 Task 모델 (status_group 프로퍼티 포함)
- `TaskCreate`: Task 생성 요청 모델
- `TaskUpdate`: Task 수정 요청 모델
- `TaskFilter`: Task 필터 조건 모델

#### notion_client.py
`NotionTaskClient` 클래스:
- `__init__`: API Key, Database ID로 초기화
- `_parse_task`: Notion 페이지 → Task 모델 변환
- `_build_properties`: Task 데이터 → Notion 속성 변환
- `_build_filter`: TaskFilter → Notion 필터 쿼리 변환
- `get_task`: 단건 조회
- `list_tasks`: 목록 조회 (필터, 페이지네이션)
- `create_task`: 생성
- `update_task`: 수정
- `delete_task`: 삭제 (아카이브)
- `batch_update_status`: 상태 일괄 변경
- `batch_update_assignee`: 담당자 일괄 변경

#### tools/task_tools.py
`register_task_tools(server, client)` 함수:
- `list_tools()`: 7개 MCP Tool 스키마 정의
- `call_tool(name, arguments)`: Tool 호출 핸들러

#### server.py
- `create_server()`: Server 인스턴스 생성, NotionTaskClient 초기화, Tool 등록
- `run_server()`: stdio_server로 MCP 서버 실행
- `main()`: 엔트리포인트

### Data Flow
```
MCP Client → call_tool() → NotionTaskClient.method() → Notion API
                ↓
         Task 모델로 변환
                ↓
         JSON 응답 반환
```

### Testing Strategy
- 통합 테스트 중심 (실제 Notion API 사용)
- pytest 사용
- 테스트용 Notion DB 별도 구성 권장

### Git Workflow
- main 브랜치: 안정 버전
- feature/* 브랜치: 기능 개발
- 커밋 메시지: conventional commits (feat:, fix:, docs: 등)

## Domain Context

### Notion Task DB Schema

| 속성명 | Notion 타입 | 설명 |
|--------|-------------|------|
| No | Unique ID (자동생성) | Jira 티켓 ID와 같은 개념 |
| 제목 | Title | 티켓 제목 |
| 타입 | Select | Task, Epic, Issue, Project |
| 상태 | Status | 할일/진행중/완료 그룹 (아래 상세) |
| 우선순위 | Select | 낮음, 중간, 높음 |
| 담당자 | Person | 담당자 지정 |
| 생성자 | Created by | 티켓 생성자 |
| 시작일 | Date | 작업 시작일 |
| 종료일 | Date | 작업 종료일 |
| period | Formula | 시작일~종료일 기간 계산 |
| 라벨 | Multi-select | 분류 태그 |
| 서비스 | Multi-select | 서비스/도메인 분류 |
| 상위항목 | Relation (Self) | 부모 Task 참조 |
| 하위항목 | Relation (Self) | 자식 Task 참조 |

### 상태(Status) 상세
```
할일 (Todo)
├── 보류
└── 시작전

진행 중 (In Progress)
└── 진행중

완료 (Done)
├── 완료
├── 배포됨
└── 보관
```

### MCP 제공 기능
1. **CRUD**: Task 생성, 조회, 수정, 삭제
2. **필터/검색**: 상태, 타입, 담당자, 우선순위, 날짜 등으로 필터링
3. **일괄 처리**: 여러 Task 동시 상태 변경, 담당자 일괄 지정

## Important Constraints
- Notion API Rate Limit: 평균 3 requests/sec
- 환경변수로 `NOTION_API_KEY`, `NOTION_DATABASE_ID` 필요
- Notion Integration이 해당 DB에 접근 권한 필요

## External Dependencies
- **Notion API**: https://developers.notion.com/
- **MCP Protocol**: https://modelcontextprotocol.io/

## Development Commands

### 환경 설정
```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

### 코드 품질
```bash
mypy src                    # 타입 체크
ruff check src              # 린트
ruff check --fix src        # 린트 자동 수정
```

### 테스트
```bash
pytest tests/ -v            # 통합 테스트 (Notion API 연동 필요)
```

### 서버 실행
```bash
notion-task-mcp             # MCP 서버 실행
```
