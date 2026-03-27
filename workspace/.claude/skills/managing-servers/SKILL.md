---
name: managing-servers
description: Manage remote servers via SSH with security hardening, user management, key rotation, and monitoring. Use when administering Linux servers remotely. Includes critical safety protocols to prevent lockouts.
---

# Managing Servers - SSH Administration

This skill provides secure server management workflows with built-in safety protocols to prevent admin lockout.

## ⚠️ CRITICAL SAFETY RULE

**NEVER remove or disable admin access without:**
1. **Explicit warning** to user about potential lockout
2. **User confirmation** to proceed
3. **Verification** that backup access exists
4. **Testing** backup access in separate session

**This rule applies to:**
- Disabling password authentication
- Removing SSH keys
- Changing SSH port
- Modifying sudo access
- Firewall rule changes
- Account deletions

## Context Import

SSH security best practices:
@../../docs/servers/ssh-security.md (if exists)

Follow project conventions:
@../../project.md

## Overview

Secure SSH server management including:
- SSH security hardening
- User and access management
- SSH key rotation
- Connection troubleshooting
- Server monitoring
- Backup access verification

**Security Principles**:
1. Public key authentication > passwords
2. Principle of least privilege
3. Defense in depth
4. Always maintain backup access
5. Test before finalizing changes

## Pre-Flight Safety Checklist

**BEFORE ANY CRITICAL OPERATIONS, VERIFY**:

```bash
# 1. Current access working
ssh user@server 'echo "Access confirmed"'

# 2. You have sudo access
ssh user@server 'sudo -v && echo "Sudo confirmed"'

# 3. Backup access method exists
# - Another SSH key?
# - Another user account?
# - Console access (physical/VNC/cloud dashboard)?

# 4. Server details documented
echo "Server: $SERVER_IP
User: $USER
Key: $SSH_KEY_PATH
Port: $SSH_PORT" > server-access.txt
```

⚠️ **NEVER proceed if ANY check fails**

## Workflow: SSH Security Hardening

**Degree of Freedom**: Low (exact sequence required for safety)

### ⚠️ WARNING: Read Entire Workflow Before Starting

This workflow modifies SSH authentication. **Incorrect execution WILL lock you out.**

**Prerequisites**:
- [ ] Current SSH access verified
- [ ] Backup SSH key exists
- [ ] Emergency access method available (console/dashboard)
- [ ] Server changes can be reverted if needed

### Step 1: Verify Current Access

```bash
# Test connection
ssh user@server 'hostname && date'

# Expected: Server hostname and current time
# If fails: STOP - Fix access first
```

### Step 2: Create Backup SSH Key

```bash
# Generate backup key
ssh-keygen -t ed25519 -f ~/.ssh/backup_key_$(date +%Y%m%d) \
  -C "backup-key-$(date +%Y%m%d)"

# Add passphrase when prompted (RECOMMENDED)
```

### Step 3: Add Backup Key to Server

```bash
# Copy backup key to server
ssh-copy-id -i ~/.ssh/backup_key_$(date +%Y%m%d) user@server

# Verify backup key added
ssh user@server 'cat ~/.ssh/authorized_keys | wc -l'
# Should show at least 2 keys now
```

### Step 4: Test Backup Key Access (CRITICAL)

```bash
# Open NEW terminal window
# Test backup key works
ssh -i ~/.ssh/backup_key_$(date +%Y%m%d) user@server 'echo "Backup access OK"'

# Expected: "Backup access OK"
# ⚠️ If fails: STOP - Fix backup key before continuing
```

**DO NOT proceed to Step 5 until backup key tested successfully**

### Step 5: Harden SSH Configuration

⚠️ **WARNING TO USER REQUIRED**

Before executing, display this warning:

```
⚠️  CRITICAL SECURITY CHANGE WARNING

This will modify SSH configuration:
- Disable password authentication
- Disable root login
- Change SSH port (optional)

RISK: If backup access not working, you will be LOCKED OUT.

Verified backup access: [YES/NO]
Emergency access available: [YES/NO]

Type 'PROCEED' to continue or 'CANCEL' to abort:
```

**WAIT FOR USER CONFIRMATION before continuing**

If user confirms 'PROCEED':

```bash
# Backup current SSH config
ssh user@server 'sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.$(date +%Y%m%d)'

# Create hardened config
ssh user@server 'sudo tee /etc/ssh/sshd_config.new' <<'EOF'
# SSH Hardening Configuration
# Generated: $(date)

# Network
Port 22                          # Change after testing
AddressFamily inet               # IPv4 only
ListenAddress 0.0.0.0

# Authentication
PermitRootLogin no               # Disable root login
PubkeyAuthentication yes         # Enable key auth
PasswordAuthentication no        # Disable password auth
PermitEmptyPasswords no
ChallengeResponseAuthentication no

# Security
UsePAM yes
X11Forwarding no
PrintMotd no
AcceptEnv LANG LC_*
Subsystem sftp /usr/lib/openssh/sftp-server

# Connection
ClientAliveInterval 300
ClientAliveCountMax 2
MaxAuthTries 3
MaxSessions 10
EOF

# Validate new config
ssh user@server 'sudo sshd -t -f /etc/ssh/sshd_config.new'

# Expected: No output (valid config)
# If errors: STOP - Fix config before applying
```

### Step 6: Apply Configuration with Safety Net

```bash
# Apply new config
ssh user@server 'sudo cp /etc/ssh/sshd_config.new /etc/ssh/sshd_config'

# Reload SSH (NOT restart - keeps connection alive)
ssh user@server 'sudo systemctl reload sshd'

# Current session stays connected
```

### Step 7: Test New Configuration (CRITICAL)

```bash
# Open ANOTHER NEW terminal window
# Test connection with new config
ssh user@server 'echo "New config works"'

# Expected: "New config works"
# If fails: IMMEDIATE ROLLBACK (Step 8)
```

**Keep original SSH session open until test succeeds**

### Step 8: Rollback Procedure (if Step 7 fails)

```bash
# In ORIGINAL terminal (still connected):

# Restore backup config
ssh user@server 'sudo cp /etc/ssh/sshd_config.backup.$(date +%Y%m%d) /etc/ssh/sshd_config'

# Reload SSH
ssh user@server 'sudo systemctl reload sshd'

# Test access restored
# Open new terminal and test connection

# Analyze what went wrong before retrying
```

### Step 9: Verification & Finalization

```bash
# Verify security settings active
ssh user@server 'sudo sshd -T | grep -E "passwordauthentication|permitrootlogin|pubkeyauthentication"'

# Expected output:
# passwordauthentication no
# permitrootlogin no
# pubkeyauthentication yes

# Document change
echo "$(date): SSH hardened on $SERVER_IP" >> server-changes.log
```

### Step 10: Additional Hardening (Optional)

**Change SSH Port** (reduces automated attacks):

⚠️ **WARNING TO USER REQUIRED**

```
⚠️  SSH PORT CHANGE WARNING

Changing SSH port requires:
1. Firewall rule update
2. Reconnection with new port
3. Update of all connection configs

Current port: 22
New port: [USER SPECIFIED]

Type 'PROCEED' to continue or 'CANCEL' to abort:
```

If user confirms:

```bash
# Update SSH config
ssh user@server "sudo sed -i 's/^Port 22/Port 2222/' /etc/ssh/sshd_config"

# Update firewall
ssh user@server 'sudo ufw allow 2222/tcp'
ssh user@server 'sudo ufw reload'

# Reload SSH
ssh user@server 'sudo systemctl reload sshd'

# Test new port (in new terminal)
ssh -p 2222 user@server 'echo "New port works"'

# If successful, remove old port from firewall
ssh -p 2222 user@server 'sudo ufw delete allow 22/tcp'

# Update connection configs
# ~/.ssh/config, scripts, documentation, etc.
```

**Install Fail2Ban** (auto-ban brute force attempts):

```bash
ssh user@server 'sudo apt-get update && sudo apt-get install -y fail2ban'

# Configure for SSH
ssh user@server 'sudo tee /etc/fail2ban/jail.local' <<'EOF'
[sshd]
enabled = true
port = 22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
EOF

# Start fail2ban
ssh user@server 'sudo systemctl enable fail2ban'
ssh user@server 'sudo systemctl start fail2ban'

# Verify running
ssh user@server 'sudo fail2ban-client status sshd'
```

## Workflow: User Management

### Adding New User with SSH Access

**Safety Level**: Medium (can lock out if modifying current user)

```bash
# 1. Create user
ssh user@server 'sudo adduser newuser'

# 2. Add to sudo group (if admin needed)
ssh user@server 'sudo usermod -aG sudo newuser'

# 3. Create SSH directory
ssh user@server 'sudo mkdir -p /home/newuser/.ssh'
ssh user@server 'sudo chmod 700 /home/newuser/.ssh'

# 4. Add user's public key
# (Get public key from user first)
echo "USER_PUBLIC_KEY" | ssh user@server 'sudo tee -a /home/newuser/.ssh/authorized_keys'

# 5. Set permissions
ssh user@server 'sudo chmod 600 /home/newuser/.ssh/authorized_keys'
ssh user@server 'sudo chown -R newuser:newuser /home/newuser/.ssh'

# 6. Test new user access
# Have user test: ssh newuser@server
```

### Removing User

⚠️ **WARNING REQUIRED if removing admin user**

```bash
# Check if user has active sessions
ssh user@server 'who | grep username_to_remove'

# If removing admin user, display warning:
```

⚠️  ADMIN USER REMOVAL WARNING

You are about to remove user with sudo access: [USERNAME]

This will:
- Delete user account
- Remove home directory
- Revoke all access

Ensure another admin user exists with verified access.

Type 'PROCEED [USERNAME]' to confirm:
```

If confirmed:

```bash
# Remove user (keep home directory as backup)
ssh user@server 'sudo deluser --remove-home username_to_remove'

# Or keep home directory
ssh user@server 'sudo deluser username_to_remove'
```

## Workflow: SSH Key Rotation

**Safety Level**: HIGH - Can cause lockout if not careful

### ⚠️ Pre-Rotation Safety Check

```bash
# 1. Verify current key works
ssh user@server 'echo "Current key OK"'

# 2. Check how many keys authorized
ssh user@server 'cat ~/.ssh/authorized_keys | grep -c "^ssh"'
# Should be at least 2 (current + backup)

# 3. If only 1 key: ADD backup key first (see Hardening Step 2-4)
```

⚠️ **NEVER rotate if only one key exists**

### Rotation Steps

```bash
# 1. Generate new key
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_new -C "rotated-$(date +%Y%m%d)"

# 2. Add new key to server
ssh-copy-id -i ~/.ssh/id_ed25519_new user@server

# 3. Test new key (NEW terminal)
ssh -i ~/.ssh/id_ed25519_new user@server 'echo "New key works"'

# Expected: "New key works"
# ⚠️ If fails: STOP - Fix new key before removing old

# 4. ONLY AFTER TEST SUCCEEDS: Remove old key
OLD_KEY_FINGERPRINT=$(ssh-keygen -lf ~/.ssh/id_ed25519_old.pub | awk '{print $2}')

ssh user@server "sed -i.backup '/$OLD_KEY_FINGERPRINT/d' ~/.ssh/authorized_keys"

# 5. Verify old key removed
ssh user@server 'cat ~/.ssh/authorized_keys | wc -l'

# 6. Update SSH config to use new key
# Update ~/.ssh/config, scripts, documentation
```

## Workflow: Connection Troubleshooting

### Cannot Connect

```bash
# 1. Test basic connectivity
ping -c 3 server_ip

# 2. Test SSH port accessible
nc -zv server_ip 22

# 3. Verbose SSH connection attempt
ssh -vvv user@server

# Look for:
# - Connection refused: Server not listening
# - Connection timeout: Firewall blocking
# - Permission denied (publickey): Key issue
# - Permission denied (password): Password disabled

# 4. If using non-standard port
ssh -vvv -p 2222 user@server

# 5. Try different key explicitly
ssh -vvv -i ~/.ssh/specific_key user@server
```

### Permission Denied (publickey)

```bash
# 1. Verify key exists locally
ls -la ~/.ssh/id_*

# 2. Check key permissions
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# 3. Verify key in authorized_keys (if have access)
ssh user@server 'cat ~/.ssh/authorized_keys'

# 4. Check server-side permissions (via console/another user)
# authorized_keys must be 600
# .ssh directory must be 700
# Home directory must not be world-writable
```

### Connection Timeout

```bash
# 1. Check server is up
ping server_ip

# 2. Check firewall allows SSH
# On server (via console):
sudo ufw status
sudo ufw allow 22/tcp  # or custom port

# 3. Check cloud provider security groups
# AWS: EC2 -> Security Groups -> Inbound rules
# Azure: VM -> Networking -> Inbound port rules
# GCP: VPC -> Firewall rules
```

## Workflow: Server Monitoring

### Security Monitoring

```bash
# 1. Check active SSH sessions
ssh user@server 'who'

# 2. Check recent logins
ssh user@server 'last -n 20'

# 3. Check failed login attempts
ssh user@server 'sudo grep "Failed password" /var/log/auth.log | tail -20'

# 4. Check fail2ban status (if installed)
ssh user@server 'sudo fail2ban-client status sshd'

# 5. Check authorized keys not modified
ssh user@server 'ls -la ~/.ssh/authorized_keys'
```

### System Health

```bash
# 1. System uptime and load
ssh user@server 'uptime'

# 2. Disk usage
ssh user@server 'df -h'

# 3. Memory usage
ssh user@server 'free -h'

# 4. CPU usage
ssh user@server 'top -bn1 | head -20'

# 5. Critical service status
ssh user@server 'sudo systemctl status sshd nginx postgresql'
```

## Emergency Access Recovery

### If Locked Out

**Try These in Order**:

1. **Backup SSH Key**:
   ```bash
   ssh -i ~/.ssh/backup_key user@server
   ```

2. **Different User Account**:
   ```bash
   ssh alternate_user@server
   ```

3. **Cloud Provider Console**:
   - AWS: EC2 Instance Connect or Session Manager
   - Azure: Bastion or Serial Console
   - GCP: SSH-in-browser from console

4. **Physical/VNC Access**:
   - Login directly to console
   - Fix SSH configuration
   - Restart SSH service

### Recovery Steps (Console Access)

```bash
# 1. Login via console

# 2. Check SSH service status
sudo systemctl status sshd

# 3. If service down, start it
sudo systemctl start sshd

# 4. Check SSH config for errors
sudo sshd -t

# 5. If config broken, restore backup
sudo cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
sudo systemctl restart sshd

# 6. Re-add your SSH key manually
sudo vi /home/user/.ssh/authorized_keys
# Paste your public key

# 7. Fix permissions
sudo chmod 700 /home/user/.ssh
sudo chmod 600 /home/user/.ssh/authorized_keys
sudo chown -R user:user /home/user/.ssh

# 8. Test SSH access from remote machine
```

## Best Practices

### Security

✓ **Always** use SSH keys over passwords
✓ **Always** maintain multiple access methods
✓ **Always** test changes in new session before closing original
✓ **Always** backup configurations before changing
✓ **Always** use strong key types (ed25519 or RSA 4096)
✓ Enable 2FA/MFA where supported
✓ Use fail2ban or similar for brute force protection
✓ Regular key rotation (90-180 days)
✓ Monitor logs for suspicious activity
✓ Keep SSH software updated

### Safety

✓ **Test backup access before critical changes**
✓ **Never close original session until new config tested**
✓ **Always have emergency access method**
✓ Document server access details securely
✓ Use configuration management (Ansible/Terraform) for reproducibility
✓ Schedule maintenance windows for changes
✓ Keep backups of SSH configs
✓ Know how to access console/physical access

### Don'ts

✗ **Never** remove last admin access
✗ **Never** disable password auth without key auth working
✗ **Never** change SSH port without firewall update
✗ **Never** remove all authorized_keys
✗ **Never** modify production without testing
✗ **Never** skip backup access verification
✗ **Never** assume changes worked without testing
✗ **Never** use weak passwords for key passphrases
✗ **Never** share private keys
✗ **Never** commit private keys to version control

## Troubleshooting

### "Permission denied (publickey)"

**Cause**: SSH key not authorized or not being used
**Solutions**:
1. Verify key added: `ssh user@server 'cat ~/.ssh/authorized_keys | grep "$(cat ~/.ssh/id_ed25519.pub)"'`
2. Check local key exists: `ls -la ~/.ssh/id_ed25519`
3. Specify key explicitly: `ssh -i ~/.ssh/id_ed25519 user@server`
4. Check server-side permissions (600 for authorized_keys, 700 for .ssh)

### "Connection refused"

**Cause**: SSH service not running or wrong port
**Solutions**:
1. Check service: `ssh user@server 'sudo systemctl status sshd'` (via console)
2. Try standard port: `ssh -p 22 user@server`
3. Try custom port: `ssh -p 2222 user@server`
4. Check firewall: `ssh user@server 'sudo ufw status'` (via console)

### "Connection timed out"

**Cause**: Firewall blocking or server down
**Solutions**:
1. Ping server: `ping server_ip`
2. Check cloud security groups
3. Verify SSH port in firewall rules
4. Check server is running (cloud dashboard)

### Locked Out Completely

**Cause**: SSH misconfiguration or all keys removed
**Solutions**:
1. Use cloud provider console/bastion
2. Use physical/VNC access
3. Restore SSH config from backup
4. Manually add SSH key via console
5. Contact hosting provider support

## Security Checklist

**Initial Server Setup**:
- [ ] Create non-root user with sudo
- [ ] Add SSH key for new user
- [ ] Test new user access
- [ ] Disable root SSH login
- [ ] Disable password authentication
- [ ] Change SSH port (optional)
- [ ] Configure firewall (ufw/iptables)
- [ ] Install fail2ban
- [ ] Set up automatic security updates
- [ ] Configure NTP for time sync

**Regular Maintenance**:
- [ ] Review active users monthly
- [ ] Rotate SSH keys quarterly
- [ ] Review authorized_keys files
- [ ] Check fail2ban logs
- [ ] Monitor auth logs for suspicious activity
- [ ] Update SSH software
- [ ] Test backup access methods
- [ ] Review sudo access grants
- [ ] Audit firewall rules
- [ ] Document configuration changes

**Before Major Changes**:
- [ ] Verify current access
- [ ] Create backup SSH key
- [ ] Test backup access
- [ ] Backup current configuration
- [ ] Schedule maintenance window
- [ ] Notify team of planned changes
- [ ] Prepare rollback procedure
- [ ] Have emergency access ready

## References

See also:
- SSH Best Practices: https://www.ssh.com/academy/ssh/best-practices
- OpenSSH Hardening: https://www.cyberciti.biz/tips/linux-unix-bsd-openssh-server-best-practices.html
- Fail2Ban Documentation: https://www.fail2ban.org/wiki/index.php/Main_Page
- `scripts/ssh-hardening-check.sh` - Automated security check script
- `scripts/backup-access-test.sh` - Verify backup access works
