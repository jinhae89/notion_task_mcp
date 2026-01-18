# Notion Task MCP

Notion API를 활용한 Task 관리 MCP(Model Context Protocol) 서버입니다.
AI 어시스턴트(Claude 등)가 팀의 Notion Task DB를 직접 조회하고 관리할 수 있게 해줍니다.

---

## 목차

- [기술 스택](#기술-스택)
- [동작 방식](#동작-방식)
- [요구사항](#요구사항)
- [설치](#설치)
- [설정](#설정)
- [MCP 클라이언트 설정](#mcp-클라이언트-설정)
- [제공 도구](#제공-도구)
- [Task DB 스키마](#task-db-스키마)
- [개발 가이드](#개발-가이드)
- [트러블슈팅](#트러블슈팅)

---

## 기술 스택

| 구분 | 기술 | 버전 | 설명 |
|------|------|------|------|
| **Language** | Python | >= 3.11 | async/await, 타입 힌트 활용 |
| **MCP SDK** | mcp | >= 1.0.0 | Model Context Protocol 공식 Python SDK |
| **Notion SDK** | notion-client | >= 2.0.0 | Notion 공식 Python SDK (async 지원) |
| **Validation** | Pydantic | >= 2.0.0 | 데이터 모델 및 유효성 검사 |
| **Env** | python-dotenv | >= 1.0.0 | 환경변수 관리 |
| **Build** | hatchling | - | PEP 517 빌드 백엔드 |

### 개발 의존성

| 구분 | 기술 | 설명 |
|------|------|------|
| **Test** | pytest, pytest-asyncio | 비동기 테스트 지원 |
| **Type Check** | mypy | 정적 타입 검사 |
| **Lint** | ruff | 빠른 Python 린터 |

---

## 동작 방식

```
┌─────────────────┐     MCP Protocol      ┌─────────────────┐     Notion API     ┌─────────────────┐
│   MCP Client    │ ◄──────────────────► │  Notion Task    │ ◄────────────────► │   Notion DB     │
│ (Claude Desktop │     (stdio/JSON)      │   MCP Server    │     (HTTPS)        │   (Task 관리)    │
│   Claude Code)  │                       │                 │                    │                 │
└─────────────────┘                       └─────────────────┘                    └─────────────────┘
```

1. **MCP Client** (Claude Desktop, Claude Code 등)가 MCP 프로토콜로 서버에 도구 호출 요청
2. **MCP Server**가 요청을 파싱하고 Notion API를 통해 DB 조작
3. 결과를 JSON 형태로 MCP Client에 반환
4. AI 어시스턴트가 결과를 해석하여 사용자에게 응답

### MCP(Model Context Protocol)란?

Anthropic이 개발한 AI 어시스턴트와 외부 도구 간의 표준 통신 프로토콜입니다.
이 프로토콜을 통해 Claude가 Notion, GitHub, Slack 등 다양한 서비스와 안전하게 상호작용할 수 있습니다.

---

## 요구사항

- **Python**: 3.11 이상
- **Notion 계정**: Task DB가 있는 워크스페이스
- **Notion Integration**: API 접근을 위한 Internal Integration
- **MCP Client**: Claude Desktop 또는 Claude Code

---

## 설치

### 1. 저장소 클론

```bash
git clone <repository-url>
cd notion_task_mcp
```

### 2. 가상환경 생성 (권장)

```bash
# uv 사용 시 (권장)
uv venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 또는 venv 사용 시
python -m venv .venv
source .venv/bin/activate
```

### 3. 패키지 설치

```bash
# uv 사용 시 (권장)
uv pip install -e .

# pip 사용 시
pip install -e .
```

### 4. 설치 확인

```bash
notion-task-mcp --help
# 또는
python -m notion_task_mcp.server
```

---

## 설정

### 1. Notion Integration 생성

1. [Notion Integrations](https://www.notion.so/my-integrations) 페이지 접속
2. **+ New integration** 클릭
3. 설정:
   - **Name**: `Task MCP` (원하는 이름)
   - **Associated workspace**: Task DB가 있는 워크스페이스 선택
   - **Capabilities**:
     - ✅ Read content
     - ✅ Update content
     - ✅ Insert content
4. **Submit** → **Internal Integration Secret** 복사 (나중에 사용)

### 2. Database ID 확인

Notion에서 Task DB 페이지 열기 → URL에서 Database ID 추출:

```
https://www.notion.so/workspace/1234567890abcdef1234567890abcdef?v=...
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                      이 부분이 Database ID
```

### 3. Integration에 DB 접근 권한 부여

**중요: 이 단계를 빠뜨리면 API 호출이 실패합니다!**

1. Notion에서 Task DB 페이지 열기
2. 우측 상단 `···` 클릭
3. **Connections** → **Connect to** → 생성한 Integration 선택

---

## MCP 클라이언트 설정

> **핵심**: Notion API Key와 Database ID는 여기서 설정합니다.

### Claude Desktop

설정 파일 위치:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "notion-task": {
      "command": "/path/to/.venv/bin/notion-task-mcp",
      "env": {
        "NOTION_API_KEY": "secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "NOTION_DATABASE_ID": "1234567890abcdef1234567890abcdef"
      }
    }
  }
}
```

> **팁**: `command`에는 가상환경 내의 실행 파일 절대 경로를 사용하세요.

### Claude Code

`.claude/settings.json` 또는 전역 설정 (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "notion-task": {
      "command": "notion-task-mcp",
      "env": {
        "NOTION_API_KEY": "secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "NOTION_DATABASE_ID": "1234567890abcdef1234567890abcdef"
      }
    }
  }
}
```

### 설정 확인

Claude에서 다음과 같이 테스트:

```
"Notion Task 목록을 보여줘"
"진행 중인 Task가 뭐가 있어?"
```

---

## 제공 도구

| 도구 | 설명 | 주요 파라미터 |
|------|------|--------------|
| `get_task` | Task 단건 조회 | `task_id` |
| `list_tasks` | Task 목록 조회 | `status`, `task_type`, `assignee`, `priority`, `labels`, `services`, 날짜 범위 등 |
| `create_task` | Task 생성 | `title` (필수), `task_type`, `status`, `priority`, `assignee`, `labels` 등 |
| `update_task` | Task 수정 | `task_id` (필수), 수정할 필드들 |
| `delete_task` | Task 삭제 (아카이브) | `task_id` |
| `batch_update_status` | 여러 Task 상태 일괄 변경 | `task_ids`, `status` |
| `batch_update_assignee` | 여러 Task 담당자 일괄 변경 | `task_ids`, `assignee` |

### 사용 예시

```
# 조회
"오늘 마감인 Task 목록 보여줘"
"높은 우선순위 Task 중 진행 중인 것들 알려줘"

# 생성
"새 Task 만들어줘: API 문서 작성, 우선순위 높음, 라벨은 문서"

# 수정
"TASK-123 상태를 완료로 변경해줘"

# 일괄 처리
"TASK-001, TASK-002, TASK-003 담당자를 홍길동으로 변경해줘"
```

---

## Task DB 스키마

MCP가 기대하는 Notion DB 속성:

| 속성명 | Notion 타입 | 필수 | 설명 |
|--------|-------------|------|------|
| No | Unique ID | - | 자동 생성 ID |
| 제목 | Title | ✅ | Task 제목 |
| 타입 | Select | - | Task, Epic, Issue, Project |
| 상태 | Status | - | 할일/진행중/완료 그룹 |
| 우선순위 | Select | - | 낮음, 중간, 높음 |
| 담당자 | Person | - | 담당자 |
| 생성자 | Created by | - | 생성자 (자동) |
| 시작일 | Date | - | 시작일 |
| 종료일 | Date | - | 종료일 |
| 라벨 | Multi-select | - | 분류 태그 |
| 서비스 | Multi-select | - | 서비스/도메인 |
| 상위항목 | Relation (Self) | - | 부모 Task |
| 하위항목 | Relation (Self) | - | 자식 Task |

### 상태 그룹

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

---

## 개발 가이드

### 개발 환경 설정

```bash
# 개발 의존성 포함 설치
uv pip install -e ".[dev]"
```

### 로컬 테스트용 환경변수 (개발자 전용)

MCP 클라이언트 없이 직접 서버를 실행하거나 테스트할 때만 필요:

```bash
cp .env.example .env
# .env 파일에 NOTION_API_KEY, NOTION_DATABASE_ID 입력
```

### 코드 품질 검사

```bash
# 타입 체크
mypy src

# 린트
ruff check src

# 린트 자동 수정
ruff check --fix src
```

### 테스트

```bash
# 통합 테스트 실행 (실제 Notion API 사용)
# .env 설정 필요
pytest tests/ -v
```

### 프로젝트 구조

```
notion_task_mcp/
├── src/notion_task_mcp/
│   ├── __init__.py
│   ├── server.py           # MCP 서버 엔트리포인트
│   ├── notion_client.py    # Notion API 래퍼
│   ├── models.py           # Pydantic 데이터 모델
│   └── tools/
│       ├── __init__.py
│       └── task_tools.py   # MCP Tool 정의
├── tests/
│   └── test_integration.py
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 트러블슈팅

### "NOTION_API_KEY가 필요합니다" 오류

- MCP 클라이언트 설정 파일의 `env` 섹션에 `NOTION_API_KEY`가 올바르게 입력되었는지 확인
- 설정 파일 저장 후 Claude Desktop/Code 재시작

### "Could not find database" 오류

- Database ID가 올바른지 확인 (URL에서 정확히 추출)
- Integration이 해당 DB에 연결되어 있는지 확인

### MCP 서버가 연결되지 않음

1. `notion-task-mcp` 명령이 실행되는지 터미널에서 직접 확인
2. Claude Desktop/Code 재시작
3. 설정 파일의 `command` 경로가 올바른지 확인

### Rate Limit 오류

Notion API는 평균 3 requests/sec 제한이 있습니다.
대량의 Task를 처리할 때는 일괄 처리 도구 사용을 권장합니다.

---

## 라이선스

[MIT License](LICENSE)
