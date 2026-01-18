# Project Context

## Purpose
Notion API를 활용한 Task 관리 MCP(Model Context Protocol) 서버.
Jira와 유사한 티켓 기반 일감 관리 시스템을 Notion DB로 구현하고, AI 어시스턴트가 이를 조회/관리할 수 있도록 MCP 인터페이스를 제공한다.

## Tech Stack
- **Language**: Python 3.11+
- **MCP SDK**: mcp (공식 Python SDK)
- **Notion Client**: notion-client (공식 Python SDK)
- **Notion API Version**: 2025-09-03 (템플릿 기능 지원)
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
- `TaskType`: Project, Task, Issue, Epic
- `TaskStatus`: 보류, 시작 전, 진행 중, 완료, 배포됨, 보관 (⚠️ 띄어쓰기 주의)
- `StatusGroup`: to_do, in_progress, complete (Notion 내부 값)
- `Priority`: 낮음, 중간, 높음
- `TaskLabel`: Mobile, Web, 기획, 디자인, 다국어, Backend
- `TaskService`: ERP, WIM Service, 자사몰, WIM Admin, 글로벌홈페이지
- `STATUS_GROUP_MAP`: 상태 → 그룹 매핑 상수
- `Task`: 메인 Task 모델 (status_group 프로퍼티 포함)
  - 새 필드: url, task_no, done_date, creator_id/creator_name, period, progress
  - 시스템 필드: created_time, last_edited_time, last_edited_by
- `TaskCreate`: Task 생성 요청 모델
  - 템플릿 옵션: template_id, use_default_template
- `TaskUpdate`: Task 수정 요청 모델 (done_date 포함)
- `TaskFilter`: Task 필터 조건 모델 (has_parent 필터 추가)

#### notion_client.py
`NotionTaskClient` 클래스:
- `__init__`: API Key, Database ID로 초기화, API 버전 2025-09-03
- `_parse_task`: Notion 페이지 → Task 모델 변환
- `_build_properties`: Task 데이터 → Notion 속성 변환
- `_build_filter`: TaskFilter → Notion 필터 쿼리 변환
- `_get_data_source_id`: Database에서 data_source_id 조회 (템플릿 API용, 캐시)
- `get_task`: 단건 조회
- `list_tasks`: 목록 조회 (필터, 페이지네이션)
- `list_templates`: 템플릿 목록 조회 (Task, Issue, Project, Epic)
- `get_template_by_type`: 타입명으로 템플릿 조회 (타입별 도구용)
- `create_task`: 생성 (템플릿 옵션 지원)
- `update_task`: 수정
- `delete_task`: 삭제 (아카이브)
- `batch_update_status`: 상태 일괄 변경
- `batch_update_assignee`: 담당자 일괄 변경

#### tools/task_tools.py
`register_task_tools(server, client)` 함수:
- `list_tools()`: 11개 MCP Tool 스키마 정의
  - 기본: get_task, list_tasks, list_templates, create_task, update_task, delete_task
  - 일괄: batch_update_status, batch_update_assignee
  - 타입별: create_epic, create_project, create_issue (템플릿+타입 자동 적용)
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
| ID | Unique ID (자동생성) | Jira 티켓 ID와 같은 개념 |
| 제목 | Title | 티켓 제목 |
| 타입 | Select | Project, Task, Issue, Epic |
| 상태 | Status | to_do/in_progress/complete 그룹 (아래 상세) |
| 우선순위 | Select | 낮음, 중간, 높음 |
| 담당자 | Person | 담당자 지정 |
| 생성자 | Person | 티켓 생성자 (수동 입력) |
| 시작일 | Date | 작업 시작일 |
| 종료일 | Date | 작업 종료일 |
| Done | Date | 완료 일시 |
| Period | Formula | 시작일~종료일 기간 계산 |
| 진행율 | Formula | 하위 항목 기준 진행률 |
| 라벨 | Multi-select | Mobile, Web, 기획, 디자인, 다국어, Backend |
| 서비스 | Multi-select | ERP, WIM Service, 자사몰, WIM Admin, 글로벌홈페이지 |
| 상위 항목 | Relation (Self) | 부모 Task 참조 (⚠️ 띄어쓰기) |
| 하위 항목 | Relation (Self) | 자식 Task 참조 (⚠️ 띄어쓰기) |
| 생성 일시 | Created time | 생성 시간 (시스템) |
| 최종 편집 일시 | Last edited time | 수정 시간 (시스템) |
| 최종 편집자 | Last edited by | 수정자 (시스템) |

### 상태(Status) 상세
```
할일 (to_do)
├── 보류
└── 시작 전    # ⚠️ 띄어쓰기

진행 중 (in_progress)
└── 진행 중    # ⚠️ 띄어쓰기

완료 (complete)
├── 완료
├── 배포됨
└── 보관
```

### MCP 제공 기능
1. **CRUD**: Task 생성, 조회, 수정, 삭제
2. **필터/검색**: 상태, 타입, 담당자, 우선순위, 날짜 등으로 필터링
3. **일괄 처리**: 여러 Task 동시 상태 변경, 담당자 일괄 지정
4. **템플릿 지원**: Task/Issue/Project/Epic 템플릿으로 생성 (본문 자동 적용)
5. **타입별 전용 도구**: create_epic, create_project, create_issue (템플릿+타입 자동)

### 템플릿 기능
Notion DB에 설정된 템플릿을 사용하여 Task 생성 가능:
- `list_templates`: 사용 가능한 템플릿 목록 조회
- `create_task`에 `template_id` 또는 `use_default_template` 옵션 전달
- 템플릿 사용 시 페이지 본문(체크리스트, 섹션 등)이 자동 적용됨

**타입별 전용 도구** (권장):
| 도구 | 자동 적용 |
|------|----------|
| `create_epic` | Epic 템플릿 + Epic 타입 |
| `create_project` | Project 템플릿 + Project 타입 |
| `create_issue` | Issue 템플릿 + Issue 타입 |

**사용 가능한 템플릿**:
| 템플릿 | 용도 |
|--------|------|
| Task | 일반 작업 (기본 템플릿) |
| Issue | 버그/이슈 트래킹 |
| Project | 프로젝트 관리 |
| Epic | 대규모 기능/에픽 |

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
