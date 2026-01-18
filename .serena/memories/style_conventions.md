# 코드 스타일 및 컨벤션

## Python 스타일
- **PEP 8** 준수
- **줄 길이**: 120자 (ruff 설정)
- **Python 버전**: 3.11+ (타입 힌트 `X | None` 문법 사용)

## 네이밍 컨벤션
- 변수/함수: `snake_case`
- 클래스: `PascalCase`
- 상수: `UPPER_SNAKE_CASE`
- 프라이빗 메서드: `_leading_underscore`

## 타입 힌트
- **필수**: 모든 함수/메서드에 타입 힌트 사용
- mypy strict 모드 적용
- Optional 대신 `X | None` 사용 (Python 3.11+)

## Docstring
- **Google 스타일** 사용
- 모든 public 클래스/함수에 docstring 작성

## 외부 라이브러리 타입 무시
```python
# notion-client, mcp SDK는 타입 스텁 이슈로 ignore 처리
@server.list_tools()  # type: ignore[no-untyped-call, untyped-decorator]
response = await self.client.databases.query(...)  # type: ignore[attr-defined]
```

## 린트 규칙 (ruff)
- E: pycodestyle errors
- F: Pyflakes
- I: isort (import 정렬)
- N: pep8-naming
- W: pycodestyle warnings
- UP: pyupgrade (최신 Python 문법)

## 커밋 메시지
- **Conventional Commits** 스타일
- 형식: `type: 설명`
- 타입: feat, fix, docs, chore, refactor, test
- Co-Authored-By 포함 시 Claude 명시
