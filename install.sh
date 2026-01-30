#!/bin/bash
# Task Skill 설치 스크립트
# 사용법: ./install.sh [설치경로]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 스크립트 위치 (프로젝트 루트)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/task"

# 기본 설치 경로 정의
CLAUDE_INSTALL_PATH="$HOME/.claude/skills/task"
ANTIGRAVITY_INSTALL_PATH="$HOME/.agent/skills/task"

# 인자 처리
if [[ "$1" == "claude" ]]; then
    TARGET_AGENT="Claude"
    INSTALL_PATH="$CLAUDE_INSTALL_PATH"
elif [[ "$1" == "antigravity" ]]; then
    TARGET_AGENT="Antigravity"
    INSTALL_PATH="$ANTIGRAVITY_INSTALL_PATH"
elif [[ "$1" =~ ^/ || "$1" =~ ^\. ]]; then
    # 경로인 경우 (기존 호환성)
    TARGET_AGENT="Custom"
    INSTALL_PATH="$1"
else
    # 선택 메뉴 표시
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}   Task Skill 설치 스크립트${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "어떤 Agent를 사용하시나요?"
    echo "1) Claude"
    echo "2) Antigravity"
    echo ""
    
    while true; do
        read -p "선택 (1/2): " choice
        case $choice in
            1)
                TARGET_AGENT="Claude"
                INSTALL_PATH="$CLAUDE_INSTALL_PATH"
                break
                ;;
            2)
                TARGET_AGENT="Antigravity"
                INSTALL_PATH="$ANTIGRAVITY_INSTALL_PATH"
                break
                ;;
            *)
                echo -e "${RED}잘못된 선택입니다. 1 또는 2를 입력해주세요.${NC}"
                ;;
        esac
    done
fi

# 소스 디렉토리 확인
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}오류: task/ 디렉토리를 찾을 수 없습니다.${NC}"
    echo "이 스크립트는 프로젝트 루트에서 실행해야 합니다."
    exit 1
fi

# ============== 의존성 검사 ==============

echo -e "${YELLOW}[1/5] 의존성 검사 중...${NC}"

# Python 버전 확인
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
            echo -e "  ${GREEN}✓${NC} Python $PYTHON_VERSION"
            return 0
        else
            echo -e "  ${RED}✗${NC} Python $PYTHON_VERSION (3.11 이상 필요)"
            return 1
        fi
    else
        echo -e "  ${RED}✗${NC} Python3를 찾을 수 없습니다"
        return 1
    fi
}

# certifi 확인
check_certifi() {
    if python3 -c "import certifi" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} certifi (SSL 인증서)"
        return 0
    else
        echo -e "  ${YELLOW}△${NC} certifi 미설치 (선택사항)"
        return 1
    fi
}

if ! check_python; then
    echo ""
    echo -e "${RED}오류: Python 3.11 이상이 필요합니다.${NC}"
    echo "Python 설치 후 다시 시도해주세요."
    exit 1
fi

if ! check_certifi; then
    echo ""
    read -p "certifi를 설치하시겠습니까? (SSL 인증서 문제 방지) [Y/n]: " install_certifi
    if [[ "$install_certifi" != "n" && "$install_certifi" != "N" ]]; then
        echo "certifi 설치 중..."
        pip3 install --user certifi
        echo -e "  ${GREEN}✓${NC} certifi 설치 완료"
    fi
fi

echo ""

# ============== 설치 경로 확인 ==============

echo -e "${YELLOW}[2/5] 설치 경로 확인...${NC}"
echo "  설치 경로: $INSTALL_PATH"

if [ -d "$INSTALL_PATH" ]; then
    echo -e "  ${YELLOW}!${NC} 기존 설치가 존재합니다."
    read -p "  덮어쓰시겠습니까? [y/N]: " overwrite
    if [[ "$overwrite" != "y" && "$overwrite" != "Y" ]]; then
        echo "설치를 취소합니다."
        exit 0
    fi
    rm -rf "$INSTALL_PATH"
fi

echo ""

# ============== API 설정 ==============

echo -e "${YELLOW}[3/5] Notion API 설정...${NC}"
echo ""

# API Key 입력 (환경변수 또는 사용자 입력)
if [[ -n "$NOTION_API_KEY" ]]; then
    echo "  Notion API Key: [환경변수로 제공됨]"
else
    while true; do
        read -p "Notion API Key: " NOTION_API_KEY
        if [[ -n "$NOTION_API_KEY" ]]; then
            break
        fi
        echo -e "  ${RED}API Key를 입력해주세요.${NC}"
    done
fi

# Database ID 입력 (환경변수 또는 사용자 입력)
if [[ -n "$NOTION_DATABASE_ID" ]]; then
    echo "  Notion Database ID: [환경변수로 제공됨]"
else
    while true; do
        read -p "Notion Database ID: " NOTION_DATABASE_ID
        if [[ -n "$NOTION_DATABASE_ID" ]]; then
            break
        fi
        echo -e "  ${RED}Database ID를 입력해주세요.${NC}"
    done
fi

echo ""

# ============== 파일 복사 ==============

echo -e "${YELLOW}[4/5] 파일 설치 중...${NC}"

# 설치 디렉토리 생성
mkdir -p "$INSTALL_PATH/scripts"

# 파일 복사
cp "$SOURCE_DIR/scripts/notion_task_cli.py" "$INSTALL_PATH/scripts/"
cp "$SOURCE_DIR/SKILL.md" "$INSTALL_PATH/"
cp "$SOURCE_DIR/config.template.json" "$INSTALL_PATH/"

# 유틸리티 스크립트 복사
cp "$SCRIPT_DIR/setup.sh" "$INSTALL_PATH/"
cp "$SCRIPT_DIR/uninstall.sh" "$INSTALL_PATH/"

# config.json 생성
cat > "$INSTALL_PATH/config.json" << EOF
{
  "notion": {
    "api_key": "$NOTION_API_KEY",
    "database_id": "$NOTION_DATABASE_ID"
  },
  "user": {
    "notion_id": "",
    "name": "",
    "email": ""
  },
  "defaults": {
    "priority": "중간",
    "type": "Task",
    "auto_assign": true
  }
}
EOF

# SKILL.md 경로 수정 (플레이스홀더를 실제 경로로 변경)
sed -i.bak "s|__INSTALL_PATH__|$INSTALL_PATH|g" "$INSTALL_PATH/SKILL.md"
rm -f "$INSTALL_PATH/SKILL.md.bak"

# 실행 권한 부여
chmod +x "$INSTALL_PATH/setup.sh"
chmod +x "$INSTALL_PATH/uninstall.sh"
chmod +x "$INSTALL_PATH/scripts/notion_task_cli.py"

echo -e "  ${GREEN}✓${NC} 파일 설치 완료"
echo ""

# ============== 사용자 설정 ==============

echo -e "${YELLOW}[5/5] 사용자 설정...${NC}"
echo ""

# setup.sh 실행
bash "$INSTALL_PATH/setup.sh" --api-key "$NOTION_API_KEY"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   설치 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "설치 경로: $INSTALL_PATH"
echo ""
echo -e "${YELLOW}다음 단계:${NC}"
echo "1. Claude Code를 재시작하세요"
echo "2. '진행중인 Task' 또는 'Task 목록'을 입력하여 테스트하세요"
echo ""
echo -e "${BLUE}문제 발생 시:${NC}"
echo "  - API 테스트: python3 $INSTALL_PATH/scripts/notion_task_cli.py list"
echo "  - 사용자 재설정: $INSTALL_PATH/setup.sh"
echo "  - 삭제: $INSTALL_PATH/uninstall.sh"
