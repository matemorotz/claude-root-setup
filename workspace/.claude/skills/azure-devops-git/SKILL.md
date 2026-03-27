---
name: azure-devops-git
description: Push code to Azure DevOps repositories with automatic credential discovery and configuration. Use when pushing commits to cetsolutions Azure DevOps, managing git authentication, or handling Azure DevOps PAT tokens.
---

# Azure DevOps Git Operations

Automated git push workflow for Azure DevOps with credential discovery and secure authentication setup.

## Overview

This skill handles pushing code to Azure DevOps repositories by:
1. Discovering existing credentials from multiple sources
2. Configuring git authentication if needed
3. Executing push operations safely
4. Managing Personal Access Tokens (PAT)

## Context Import

Reference git push documentation:
@../../GIT_PUSH_GUIDE.md

Follow project conventions:
@../../CLAUDE.md

## Credential Discovery Workflow

### Step 1: Search for Existing Credentials

Check multiple credential sources in order:

```bash
# 1. Git credential store
cat ~/.git-credentials 2>/dev/null | grep "cetsolutions"

# 2. Environment files
grep "AZURE_DEVOPS_PAT" /root/software/.env 2>/dev/null

# 3. Git config
git config --global credential.helper
git config --get-regexp credential

# 4. Azure CLI configuration
az account show 2>/dev/null
az devops configure -l 2>/dev/null
```

### Step 2: Validate Discovered Credentials

If credentials found, test them:

```bash
cd /root/software/CoreTeam/TheCoreTeam

# Test with dry-run
git push --dry-run origin simple_team_cleanup 2>&1
```

If successful: Credentials are valid, proceed to push
If fails: Need to configure new credentials

### Step 3: Configure Credentials (if needed)

**Option A: Using Environment File (.env)**

```bash
# Check if .env exists
if [ ! -f /root/software/.env ]; then
    cp /root/software/.env.example /root/software/.env
    echo "Created .env file - needs PAT configuration"
fi

# Load and verify
source /root/software/.env
if [ -z "$AZURE_DEVOPS_PAT" ]; then
    echo "AZURE_DEVOPS_PAT not set in .env"
    echo "Generate PAT at: https://dev.azure.com/cetsolutions/_usersSettings/tokens"
    exit 1
fi
```

**Option B: Using Git Credential Helper**

```bash
# Enable credential storage
git config --global credential.helper store

# First push will prompt for credentials
# Username: Azure DevOps email
# Password: Personal Access Token (PAT)
```

**Option C: Using Azure CLI**

```bash
# Login to Azure DevOps
az login
az devops configure --defaults organization=https://dev.azure.com/cetsolutions

# PAT will be requested on first git operation
```

### Step 4: Generate PAT (if needed)

Guide user to generate Personal Access Token:

**URL:** https://dev.azure.com/cetsolutions/_usersSettings/tokens

**Steps:**
1. Click "New Token"
2. Name: "Git Push - $(date +%Y-%m-%d)"
3. Organization: cetsolutions
4. Expiration: 90 days (recommended)
5. Scopes: **Code (Read, Write, & Manage)**
6. Click "Create"
7. Copy token immediately (won't be shown again)

**Save to .env:**
```bash
# Add to /root/software/.env
AZURE_DEVOPS_PAT="your-generated-token-here"
AZURE_DEVOPS_USERNAME="your-email@example.com"
```

## Push Workflow

### Step 1: Verify Repository State

```bash
cd /root/software/CoreTeam/TheCoreTeam

# Check current branch
git branch --show-current

# View unpushed commits
git log origin/simple_team_cleanup..HEAD --oneline

# Check git status
git status
```

### Step 2: Configure Git Identity (if needed)

```bash
# Check current identity
git config user.name
git config user.email

# Set if not configured
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

### Step 3: Execute Push

```bash
cd /root/software/CoreTeam/TheCoreTeam

# Push to Azure DevOps
git push origin simple_team_cleanup

# If prompted for credentials:
# Username: your-azure-devops-email@example.com
# Password: your-personal-access-token
```

### Step 4: Verify Push Success

```bash
# Check remote status
git fetch origin
git status

# Should show: "Your branch is up to date with 'origin/simple_team_cleanup'"

# View on Azure DevOps
# URL: https://cetsolutions.visualstudio.com/AiAssistant/_git/TheCoreTeam
```

## Complete Automated Workflow

Full workflow combining all steps:

```bash
#!/bin/bash
# Automated Azure DevOps git push

REPO_PATH="/root/software/CoreTeam/TheCoreTeam"
BRANCH="simple_team_cleanup"

echo "Step 1: Checking repository..."
cd "$REPO_PATH"
git status

echo "Step 2: Checking for credentials..."
if git push --dry-run origin "$BRANCH" 2>&1 | grep -q "Authentication failed"; then
    echo "Credentials needed"

    # Check .env file
    if [ -f /root/software/.env ]; then
        source /root/software/.env
        if [ -n "$AZURE_DEVOPS_PAT" ]; then
            echo "PAT found in .env"
            # Configure credential helper
            git config --global credential.helper store

            # Create credentials file
            echo "https://$AZURE_DEVOPS_USERNAME:$AZURE_DEVOPS_PAT@cetsolutions.visualstudio.com" > ~/.git-credentials
            chmod 600 ~/.git-credentials
        else
            echo "ERROR: AZURE_DEVOPS_PAT not set in /root/software/.env"
            echo "Generate PAT at: https://dev.azure.com/cetsolutions/_usersSettings/tokens"
            exit 1
        fi
    else
        echo "ERROR: /root/software/.env not found"
        echo "Copy from .env.example and add your PAT"
        exit 1
    fi
fi

echo "Step 3: Pushing to Azure DevOps..."
git push origin "$BRANCH"

if [ $? -eq 0 ]; then
    echo "✅ Push successful!"
    echo "View at: https://cetsolutions.visualstudio.com/AiAssistant/_git/TheCoreTeam"
else
    echo "❌ Push failed"
    exit 1
fi
```

## Troubleshooting

### Authentication Failed

**Cause:** Invalid or expired PAT token

**Solution:**
```bash
# Regenerate PAT
# https://dev.azure.com/cetsolutions/_usersSettings/tokens

# Update .env
nano /root/software/.env
# Set: AZURE_DEVOPS_PAT="new-token-here"

# Clear old credentials
rm ~/.git-credentials

# Retry push
cd /root/software/CoreTeam/TheCoreTeam
git push origin simple_team_cleanup
```

### Could Not Read Username

**Cause:** HTTPS remote requires credentials

**Solution:**
```bash
# Option 1: Use credential helper
git config --global credential.helper store
git push origin simple_team_cleanup
# Enter credentials when prompted

# Option 2: Use .env PAT
source /root/software/.env
echo "https://$AZURE_DEVOPS_USERNAME:$AZURE_DEVOPS_PAT@cetsolutions.visualstudio.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
git push origin simple_team_cleanup
```

### Permission Denied

**Cause:** Insufficient PAT scopes or expired token

**Solution:**
```bash
# Verify PAT has Code (Read, Write, & Manage) scope
# Regenerate if needed: https://dev.azure.com/cetsolutions/_usersSettings/tokens

# Check token expiration
# Update /root/software/.env with new token
```

### Remote Rejected

**Cause:** Branch protection or permissions issue

**Solution:**
```bash
# Check branch policies on Azure DevOps
# May need to create Pull Request instead of direct push

# Alternative: Push to new branch
git checkout -b feature/new-branch
git push origin feature/new-branch
```

## Repository Information

**Organization:** cetsolutions
**Project:** AiAssistant
**Repository:** TheCoreTeam
**URL:** https://cetsolutions.visualstudio.com/AiAssistant/_git/TheCoreTeam

**Current Branches:**
- `main` - Production branch
- `simple_team_cleanup` - Active development branch

## Security Best Practices

**PAT Token Management:**
- ✅ Store in `.env` (in .gitignore)
- ✅ Use scoped tokens (only Code permissions)
- ✅ Set expiration (90 days recommended)
- ✅ Rotate regularly
- ❌ Never commit to git
- ❌ Never share tokens
- ❌ Don't use overly broad scopes

**Credential Storage:**
```bash
# Secure credential file permissions
chmod 600 ~/.git-credentials
chmod 600 /root/software/.env

# Clear credentials when done (optional)
rm ~/.git-credentials
```

## Quick Reference

```bash
# Discover credentials
cat ~/.git-credentials | grep cetsolutions
grep AZURE_DEVOPS_PAT /root/software/.env

# Test credentials
cd /root/software/CoreTeam/TheCoreTeam
git push --dry-run origin simple_team_cleanup

# Push commits
git push origin simple_team_cleanup

# View repository online
# https://cetsolutions.visualstudio.com/AiAssistant/_git/TheCoreTeam
```

## References

- Azure DevOps Git Documentation: https://docs.microsoft.com/en-us/azure/devops/repos/git/
- PAT Token Management: https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate
- Git Credential Storage: https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage
- @../../GIT_PUSH_GUIDE.md - Complete push guide
