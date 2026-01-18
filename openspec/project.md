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
