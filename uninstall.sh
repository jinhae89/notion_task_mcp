#!/bin/bash
# Task Skill 삭제 스크립트
# 사용법: ./uninstall.sh [설치경로]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 기본 설치 경로
DEFAULT_INSTALL_PATH="$HOME/.claude/skills/task"

# 스크립트 위치 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 삭제 대상 경로 결정
if [ -f "$SCRIPT_DIR/config.json" ] && [ -f "$SCRIPT_DIR/SKILL.md" ]; then
    # 설치된 skill 디렉토리에서 실행
    TARGET_PATH="$SCRIPT_DIR"
else
    # 프로젝트 루트에서 실행 - 기본 설치 경로 사용
    TARGET_PATH="${1:-$DEFAULT_INSTALL_PATH}"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Task Skill 삭제${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 존재 확인
if [ ! -d "$TARGET_PATH" ]; then
    echo -e "${YELLOW}!${NC} 설치된 skill을 찾을 수 없습니다: $TARGET_PATH"
    exit 0
fi

echo -e "${YELLOW}삭제 대상:${NC} $TARGET_PATH"
echo ""

# 설정 백업 확인
if [ -f "$TARGET_PATH/config.json" ]; then
    echo -e "${YELLOW}설정 파일이 존재합니다.${NC}"
    read -p "설정을 백업하시겠습니까? [Y/n]: " backup_config

    if [[ "$backup_config" != "n" && "$backup_config" != "N" ]]; then
        BACKUP_PATH="$HOME/.task_skill_config_backup.json"
        cp "$TARGET_PATH/config.json" "$BACKUP_PATH"
        echo -e "  ${GREEN}✓${NC} 설정 백업 완료: $BACKUP_PATH"
        echo ""
    fi
fi

# 삭제 확인
read -p "정말로 삭제하시겠습니까? [y/N]: " confirm_delete

if [[ "$confirm_delete" != "y" && "$confirm_delete" != "Y" ]]; then
    echo "삭제를 취소합니다."
    exit 0
fi

echo ""
echo -e "${YELLOW}삭제 중...${NC}"

# 디렉토리 삭제
rm -rf "$TARGET_PATH"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   삭제 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Task Skill이 삭제되었습니다."

if [ -f "$HOME/.task_skill_config_backup.json" ]; then
    echo ""
    echo -e "${BLUE}참고:${NC} 설정 백업 파일이 저장되어 있습니다."
    echo "  위치: $HOME/.task_skill_config_backup.json"
    echo "  재설치 시 이 파일을 config.json으로 복사하여 사용할 수 있습니다."
fi

echo ""
echo "Claude Code를 재시작해주세요."
