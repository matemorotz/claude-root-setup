#!/bin/bash
#
# ssh-hardening-check.sh
# Check SSH security configuration against best practices
#
# Usage: ./ssh-hardening-check.sh user@server

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SERVER="$1"

if [ -z "$SERVER" ]; then
    echo -e "${RED}Error: Server not specified${NC}"
    echo "Usage: $0 user@server"
    exit 1
fi

echo "================================================"
echo "  SSH Security Hardening Check"
echo "================================================"
echo "Server: $SERVER"
echo ""

# Function to check setting
check_setting() {
    local name="$1"
    local expected="$2"
    local actual="$3"

    echo -n "  $name: "
    if [ "$actual" = "$expected" ]; then
        echo -e "${GREEN}✓ $actual${NC}"
        return 0
    else
        echo -e "${RED}✗ $actual (expected: $expected)${NC}"
        return 1
    fi
}

# Get SSH config
echo "Fetching SSH configuration..."
CONFIG=$(ssh "$SERVER" 'sudo sshd -T' 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to fetch SSH configuration${NC}"
    echo "Ensure you have sudo access on the server"
    exit 1
fi

echo ""

# Check critical settings
FAIL_COUNT=0

echo "Authentication Settings:"
check_setting "PasswordAuthentication" "no" "$(echo "$CONFIG" | grep "^passwordauthentication" | awk '{print $2}')" || ((FAIL_COUNT++))
check_setting "PubkeyAuthentication" "yes" "$(echo "$CONFIG" | grep "^pubkeyauthentication" | awk '{print $2}')" || ((FAIL_COUNT++))
check_setting "PermitRootLogin" "no" "$(echo "$CONFIG" | grep "^permitrootlogin" | awk '{print $2}')" || ((FAIL_COUNT++))
check_setting "PermitEmptyPasswords" "no" "$(echo "$CONFIG" | grep "^permitemptypasswords" | awk '{print $2}')" || ((FAIL_COUNT++))

echo ""
echo "Security Settings:"
check_setting "X11Forwarding" "no" "$(echo "$CONFIG" | grep "^x11forwarding" | awk '{print $2}')" || ((FAIL_COUNT++))
check_setting "MaxAuthTries" "3" "$(echo "$CONFIG" | grep "^maxauthtries" | awk '{print $2}')" || echo -e "${YELLOW}⚠ $(echo "$CONFIG" | grep "^maxauthtries" | awk '{print $2}') (recommended: 3)${NC}"

echo ""
echo "Connection Settings:"
PORT=$(echo "$CONFIG" | grep "^port" | awk '{print $2}')
echo -n "  Port: "
if [ "$PORT" = "22" ]; then
    echo -e "${YELLOW}⚠ $PORT (consider changing for security)${NC}"
else
    echo -e "${GREEN}✓ $PORT (non-standard port)${NC}"
fi

ALIVE_INTERVAL=$(echo "$CONFIG" | grep "^clientaliveinterval" | awk '{print $2}')
echo "  ClientAliveInterval: $ALIVE_INTERVAL seconds"

ALIVE_COUNT=$(echo "$CONFIG" | grep "^clientalivecountmax" | awk '{print $2}')
echo "  ClientAliveCountMax: $ALIVE_COUNT"

echo ""
echo "Additional Checks:"

# Check fail2ban
echo -n "  Fail2Ban installed: "
if ssh "$SERVER" 'sudo systemctl is-active fail2ban >/dev/null 2>&1'; then
    echo -e "${GREEN}✓ Active${NC}"
else
    echo -e "${YELLOW}⚠ Not installed/active${NC}"
    echo "    Install: sudo apt-get install fail2ban"
fi

# Check UFW firewall
echo -n "  UFW Firewall: "
if ssh "$SERVER" 'sudo ufw status | grep -q "Status: active"'; then
    echo -e "${GREEN}✓ Active${NC}"
else
    echo -e "${YELLOW}⚠ Not active${NC}"
    echo "    Enable: sudo ufw enable"
fi

# Check SSH key types
echo ""
echo "Authorized Keys Analysis:"
ssh "$SERVER" 'cat ~/.ssh/authorized_keys' | while read -r line; do
    if [[ $line =~ ^ssh- ]]; then
        KEY_TYPE=$(echo "$line" | awk '{print $1}')
        case "$KEY_TYPE" in
            "ssh-ed25519")
                echo -e "  ${GREEN}✓ $KEY_TYPE (modern, secure)${NC}"
                ;;
            "ssh-rsa")
                KEY_SIZE=$(echo "$line" | ssh-keygen -lf - 2>/dev/null | awk '{print $1}')
                if [ "$KEY_SIZE" -ge 4096 ]; then
                    echo -e "  ${GREEN}✓ $KEY_TYPE $KEY_SIZE bits (acceptable)${NC}"
                else
                    echo -e "  ${YELLOW}⚠ $KEY_TYPE $KEY_SIZE bits (upgrade to 4096+ or ed25519)${NC}"
                fi
                ;;
            "ssh-dss")
                echo -e "  ${RED}✗ $KEY_TYPE (deprecated, replace immediately)${NC}"
                ((FAIL_COUNT++))
                ;;
            *)
                echo -e "  ${YELLOW}⚠ $KEY_TYPE (unknown type)${NC}"
                ;;
        esac
    fi
done

# Summary
echo ""
echo "================================================"
echo "  Summary"
echo "================================================"

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}All critical security checks passed!${NC}"
    echo ""
    echo "✓ Password authentication disabled"
    echo "✓ Root login disabled"
    echo "✓ Public key authentication enabled"
    echo "✓ No empty passwords allowed"
    echo ""
    echo "Your SSH configuration follows security best practices."
else
    echo -e "${RED}$FAIL_COUNT critical security issue(s) found${NC}"
    echo ""
    echo "⚠️  RECOMMENDATION: Run SSH hardening workflow"
    echo "⚠️  See: managing-servers skill documentation"
fi

echo ""
