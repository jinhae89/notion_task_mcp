# 작업 완료 체크리스트

작업 완료 전 반드시 확인할 항목들:

## 1. 코드 품질
- [ ] `mypy src` - 타입 체크 통과
- [ ] `ruff check src` - 린트 체크 통과
- [ ] 필요시 `ruff check --fix src`로 자동 수정

## 2. 테스트
- [ ] 새 기능/수정에 대한 테스트 추가 (해당 시)
- [ ] `pytest tests/ -v` - 테스트 통과 (Notion API 연동 필요)

## 3. 문서화
- [ ] 새 기능에 대한 docstring 작성
- [ ] README.md 업데이트 (필요 시)
- [ ] openspec/project.md 업데이트 (아키텍처 변경 시)

## 4. Git 커밋
- [ ] 변경사항 확인: `git status`, `git diff`
- [ ] Conventional Commits 형식으로 커밋
- [ ] Co-Authored-By 태그 포함

## MCP Tool 추가/수정 시 추가 체크
- [ ] `task_tools.py`의 `list_tools()`에 Tool 정의 추가
- [ ] `call_tool()` 핸들러에 처리 로직 추가
- [ ] inputSchema JSON 스키마 정확성 확인
