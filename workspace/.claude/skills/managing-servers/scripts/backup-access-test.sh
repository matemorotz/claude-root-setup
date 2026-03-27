#!/bin/bash
#
# backup-access-test.sh
# Test backup SSH access before critical changes
#
# Usage: ./backup-access-test.sh user@server [backup_key_path]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SERVER="$1"
BACKUP_KEY="${2:-$HOME/.ssh/backup_key}"

if [ -z "$SERVER" ]; then
    echo -e "${RED}Error: Server not specified${NC}"
    echo "Usage: $0 user@server [backup_key_path]"
    exit 1
fi

echo "================================================"
echo "  SSH Backup Access Test"
echo "================================================"
echo "Server: $SERVER"
echo "Backup Key: $BACKUP_KEY"
echo ""

# Test 1: Backup key exists
echo -n "1. Checking backup key exists... "
if [ -f "$BACKUP_KEY" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "  Backup key not found at: $BACKUP_KEY"
    echo "  Create backup key:"
    echo "    ssh-keygen -t ed25519 -f $BACKUP_KEY"
    exit 1
fi

# Test 2: Backup key has correct permissions
echo -n "2. Checking backup key permissions... "
PERMS=$(stat -c %a "$BACKUP_KEY" 2>/dev/null || stat -f %A "$BACKUP_KEY" 2>/dev/null)
if [ "$PERMS" = "600" ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ Fixing${NC}"
    chmod 600 "$BACKUP_KEY"
    echo "  Fixed permissions to 600"
fi

# Test 3: Current SSH access works
echo -n "3. Testing current SSH access... "
if ssh -o ConnectTimeout=10 -o BatchMode=yes "$SERVER" 'exit' 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "  Cannot connect with current credentials"
    echo "  Fix current access before testing backup"
    exit 1
fi

# Test 4: Backup key access works
echo -n "4. Testing backup key access... "
if ssh -i "$BACKUP_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$SERVER" 'exit' 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "  Backup key cannot authenticate"
    echo "  Add backup key to server:"
    echo "    ssh-copy-id -i $BACKUP_KEY $SERVER"
    exit 1
fi

# Test 5: Verify sudo access
echo -n "5. Testing sudo access... "
if ssh -i "$BACKUP_KEY" -o BatchMode=yes "$SERVER" 'sudo -n true' 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ Limited${NC}"
    echo "  Backup key user has no passwordless sudo"
    echo "  (This may be intentional for security)"
fi

# Test 6: Count authorized keys
echo -n "6. Counting authorized SSH keys... "
KEY_COUNT=$(ssh -i "$BACKUP_KEY" "$SERVER" 'grep -c "^ssh" ~/.ssh/authorized_keys 2>/dev/null || echo 0')
if [ "$KEY_COUNT" -ge 2 ]; then
    echo -e "${GREEN}✓ ($KEY_COUNT keys)${NC}"
else
    echo -e "${YELLOW}⚠ Only $KEY_COUNT key(s)${NC}"
    echo "  Recommended: At least 2 keys for safety"
fi

# Summary
echo ""
echo "================================================"
echo "  Test Summary"
echo "================================================"
echo -e "${GREEN}Backup access is working!${NC}"
echo ""
echo "✓ Backup key exists and has correct permissions"
echo "✓ Both current and backup access tested successfully"
echo "✓ You have $KEY_COUNT authorized key(s) on the server"
echo ""
echo -e "${GREEN}SAFE to proceed with SSH configuration changes${NC}"
echo ""
echo "⚠️  IMPORTANT: Keep this terminal open during changes"
echo "⚠️  Test new configuration in a SEPARATE terminal"
echo "⚠️  Only close original session after successful test"
echo ""
