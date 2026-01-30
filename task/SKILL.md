---
name: task
description: Notion Task를 관리합니다. "진행중인 Task", "할 일 뭐야", "Task 만들어줘", "WIRB-XX 완료", "Task 현황" 등 Task 관련 요청 시 사용합니다.
allowed-tools: Bash(python3:*)
---

# Notion Task 관리

사용자의 Task 관련 요청을 처리합니다.

## CLI 도구

```bash
# 기본 명령어
python3 __INSTALL_PATH__/scripts/notion_task_cli.py list [--status STATUS] [--priority PRIORITY] [--type TYPE] [--json]
python3 __INSTALL_PATH__/scripts/notion_task_cli.py get <task_id>
python3 __INSTALL_PATH__/scripts/notion_task_cli.py create --title "제목" [--type TYPE] [--priority PRIORITY] [--assignee NOTION_ID]
python3 __INSTALL_PATH__/scripts/notion_task_cli.py update <task_id> [--status STATUS] [--priority PRIORITY] [--title TITLE] [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]
python3 __INSTALL_PATH__/scripts/notion_task_cli.py done <task_id>

# 관계 조회 (상위 항목)
python3 __INSTALL_PATH__/scripts/notion_task_cli.py projects  # 내 Project 목록
python3 __INSTALL_PATH__/scripts/notion_task_cli.py epics     # 내 Epic 목록
```

## 설정

`config.json` 파일에 모든 설정이 저장되어 있습니다:
- **Notion API**: API 키, 데이터베이스 ID
- **사용자**: config.json에서 설정
- **자동 담당자 지정**: Task 생성 시 자동으로 담당자가 지정됨
- **기본 우선순위**: 중간

## 의도별 처리

### 조회
- "진행중인 Task", "할 일 뭐야?", "오늘 할 일" → `list --status "진행 중" --type "Task"`
- "높은 우선순위 Task" → `list --priority "높음"`
- "시작 전 Task들" → `list --status "시작 전"`
- "전체 현황", "요약" → 상태별 조회 후 요약

### 타입별 조회
- "내 Project 알려줘", "프로젝트 목록" → `projects`
- "내 Epic 알려줘", "에픽 목록" → `epics`
- "Issue 목록" → `list --type "Issue"`

### 생성
- "Task 만들어줘" → 제목 확인 후 `create`
- "XXX Task 생성" → `create --title "XXX"`

### 수정
- "WIRB-XX 진행중으로" → `update <id> --status "진행 중"`
- "WIRB-XX 우선순위 높음" → `update <id> --priority "높음"`
- "WIRB-XX 시작일 오늘로" → `update <id> --start-date "YYYY-MM-DD"`

### 완료
- "WIRB-XX 완료" → `done <id>`

## 참조값

**상태**: 진행 중, 완료, 시작 전, 보류, 배포됨, 보관
**우선순위**: 높음, 중간, 낮음
**타입**: Task, Epic, Issue, Project

## 처리 지침

1. 사용자 요청에서 의도 파악
2. 필요한 정보 없으면 질문 (Task ID, 제목 등)
3. CLI 명령 실행
4. 결과 정리하여 보여주기
5. WIRB-XX 형식 ID는 list로 실제 ID 조회 후 사용

$ARGUMENTS
