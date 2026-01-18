# 개발 명령어

## 환경 설정
```bash
# 가상환경 생성 및 활성화
uv venv && source .venv/bin/activate

# 의존성 설치 (개발용 포함)
uv pip install -e ".[dev]"
```

## 서버 실행
```bash
# MCP 서버 실행
notion-task-mcp

# 또는 모듈로 실행
python -m notion_task_mcp.server
```

## 코드 품질
```bash
# 타입 체크
mypy src

# 린트 체크
ruff check src

# 린트 자동 수정
ruff check --fix src
```

## 테스트
```bash
# 통합 테스트 실행 (실제 Notion API 사용, .env 필요)
pytest tests/ -v
```

## Git
```bash
# 상태 확인
git status

# 커밋 (conventional commits 스타일)
git commit -m "feat: 새 기능 추가"
git commit -m "fix: 버그 수정"
git commit -m "chore: 설정 변경"
git commit -m "docs: 문서 수정"
```
