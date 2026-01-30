#!/bin/bash
# Task Skill 사용자 설정 스크립트
# 사용법: ./setup.sh [--api-key API_KEY]
#
# 설치된 skill에서 직접 실행하거나,
# install.sh에서 자동으로 호출됩니다.

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 스크립트 위치 확인 (설치된 위치 또는 프로젝트 루트)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# config.json 위치 결정
if [ -f "$SCRIPT_DIR/config.json" ]; then
    # 설치된 skill 디렉토리에서 실행
    CONFIG_FILE="$SCRIPT_DIR/config.json"
elif [ -f "$HOME/.claude/skills/task/config.json" ]; then
    # 프로젝트 루트에서 실행 - 기본 설치 경로 사용
    CONFIG_FILE="$HOME/.claude/skills/task/config.json"
else
    echo -e "${RED}오류: config.json을 찾을 수 없습니다.${NC}"
    echo "먼저 install.sh를 실행해주세요."
    exit 1
fi

# API Key 파라미터 처리
API_KEY=""
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --api-key) API_KEY="$2"; shift ;;
        *) ;;
    esac
    shift
done

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   사용자 설정${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# API Key 가져오기
if [ -z "$API_KEY" ]; then
    API_KEY=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['notion']['api_key'])")
fi

if [ -z "$API_KEY" ]; then
    echo -e "${RED}오류: Notion API Key가 설정되지 않았습니다.${NC}"
    exit 1
fi

# ============== 사용자 정보 입력 ==============

echo -e "${YELLOW}사용자 정보를 입력해주세요:${NC}"
echo ""

# 이름 입력 (환경변수 또는 사용자 입력)
if [[ -n "$USER_NAME" ]]; then
    echo "  이름: [환경변수로 제공됨] ($USER_NAME)"
else
    while true; do
        read -p "이름 (예: 홍길동): " USER_NAME
        if [[ -n "$USER_NAME" ]]; then
            break
        fi
        echo -e "  ${RED}이름을 입력해주세요.${NC}"
    done
fi

# 이메일 입력 (환경변수 또는 사용자 입력)
if [[ -n "$USER_EMAIL" ]]; then
     echo "  이메일: [환경변수로 제공됨] ($USER_EMAIL)"
else
    while true; do
        read -p "이메일 (예: user@company.com): " USER_EMAIL
        if [[ "$USER_EMAIL" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
            break
        fi
        echo -e "  ${RED}올바른 이메일 형식을 입력해주세요.${NC}"
    done
fi

echo ""

# ============== Notion User ID 조회 ==============

echo -e "${YELLOW}Notion User ID 조회 중...${NC}"

# Python 스크립트로 사용자 목록 조회
USERS_JSON=$(python3 << EOF
import json
import ssl
from urllib.request import Request, urlopen

try:
    import certifi
    ssl_context = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

api_key = "$API_KEY"
url = "https://api.notion.com/v1/users"

req = Request(url, headers={
    "Authorization": f"Bearer {api_key}",
    "Notion-Version": "2022-06-28"
})

try:
    with urlopen(req, context=ssl_context) as response:
        data = json.loads(response.read().decode())
        users = []
        for user in data.get("results", []):
            if user.get("type") == "person":
                users.append({
                    "id": user["id"],
                    "name": user.get("name", ""),
                    "email": user.get("person", {}).get("email", "")
                })
        print(json.dumps(users))
except Exception as e:
    print(json.dumps([]))
EOF
)

# 이메일로 사용자 찾기
FOUND_USER=$(python3 << EOF
import json

users = json.loads('$USERS_JSON')
target_email = "$USER_EMAIL".lower()

for user in users:
    if user.get("email", "").lower() == target_email:
        print(json.dumps(user))
        break
else:
    print("null")
EOF
)

USER_ID=""

if [ "$FOUND_USER" != "null" ]; then
    # 이메일로 매칭됨
    FOUND_NAME=$(echo "$FOUND_USER" | python3 -c "import json,sys; print(json.load(sys.stdin)['name'])")
    FOUND_ID=$(echo "$FOUND_USER" | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")

    echo -e "  ${GREEN}✓${NC} 사용자를 찾았습니다: $FOUND_NAME"
    USER_ID="$FOUND_ID"
else
    # 이메일로 찾지 못함 - 목록 표시
    echo -e "  ${YELLOW}!${NC} 이메일로 사용자를 찾지 못했습니다."
    echo ""

    # 사용자 목록 파싱
    USER_COUNT=$(echo "$USERS_JSON" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")

    if [ "$USER_COUNT" -gt 0 ]; then
        echo -e "${CYAN}Workspace 멤버 목록:${NC}"
        echo ""

        python3 << EOF
import json

users = json.loads('$USERS_JSON')
for i, user in enumerate(users, 1):
    name = user.get("name", "이름 없음")
    email = user.get("email", "이메일 없음")
    user_id = user.get("id", "")
    print(f"  {i}. {name} ({email})")
    print(f"     ID: {user_id}")
EOF

        echo ""
        read -p "번호를 선택하거나 User ID를 직접 입력하세요: " selection

        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -gt 0 ] && [ "$selection" -le "$USER_COUNT" ]; then
            # 번호 선택
            USER_ID=$(python3 << EOF
import json
users = json.loads('$USERS_JSON')
print(users[$selection - 1]["id"])
EOF
)
        else
            # 직접 입력
            USER_ID="$selection"
        fi
    else
        echo -e "  ${YELLOW}!${NC} Workspace 멤버를 조회할 수 없습니다."
        echo ""
        echo "Notion User ID를 직접 입력해주세요."
        echo "(Notion 설정 > 내 계정에서 확인 가능)"
        read -p "User ID: " USER_ID
    fi
fi

if [ -z "$USER_ID" ]; then
    echo -e "${RED}오류: User ID가 설정되지 않았습니다.${NC}"
    exit 1
fi

echo ""

# ============== config.json 업데이트 ==============

echo -e "${YELLOW}설정 저장 중...${NC}"

python3 << EOF
import json

with open("$CONFIG_FILE", "r", encoding="utf-8") as f:
    config = json.load(f)

config["user"]["notion_id"] = "$USER_ID"
config["user"]["name"] = "$USER_NAME"
config["user"]["email"] = "$USER_EMAIL"

with open("$CONFIG_FILE", "w", encoding="utf-8") as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("설정이 저장되었습니다.")
EOF

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   사용자 설정 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "이름: $USER_NAME"
echo "이메일: $USER_EMAIL"
echo "User ID: $USER_ID"
