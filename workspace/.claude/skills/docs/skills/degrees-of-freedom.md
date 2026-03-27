# Degrees of Freedom Guide

How to match workflow guidance specificity to task complexity and error-proneness.

## Concept

**Degrees of Freedom** = How much flexibility users have in executing a workflow

Match guidance level to:
- Task complexity
- Error consequences
- User expertise level
- Domain constraints

## Three Freedom Levels

### High Freedom (Creative/Exploratory)

**When to Use**:
- Creative tasks with multiple valid solutions
- Exploratory work where experimentation is valuable
- Design decisions without critical constraints
- Innovation and prototyping phases

**Guidance Style**:
- Present options and trade-offs
- Explain evaluation criteria
- Encourage experimentation
- Minimal prescriptive steps

**Example: Designing System Architecture**

```markdown
## Designing the Architecture

Consider these approaches:

### Microservices Architecture
**Pros**: Independent scaling, technology diversity, fault isolation
**Cons**: Complex deployment, network overhead, distributed debugging
**Best for**: Large teams, independent services, different scaling needs

### Monolithic Architecture
**Pros**: Simple deployment, easy debugging, shared codebase
**Cons**: Scaling all-or-nothing, technology lock-in, coordination overhead
**Best for**: Small teams, cohesive domain, rapid iteration

### Serverless Architecture
**Pros**: Auto-scaling, pay-per-use, no server management
**Cons**: Cold starts, vendor lock-in, debugging challenges
**Best for**: Event-driven, variable load, rapid prototyping

Evaluate based on:
- Team size and expertise
- Expected scale and traffic patterns
- Budget constraints
- Time to market requirements
- Operational complexity tolerance
```

**Example: Algorithmic Art Creation**

```markdown
## Creating Generative Art

Explore creative approaches:

**Algorithms to Consider**:
- Fractals (Mandelbrot, Julia sets)
- Noise functions (Perlin, Simplex)
- Particle systems
- Cellular automata (Conway's Life, custom rules)
- L-systems (plant-like structures)
- Randomized geometric patterns

**Visual Elements**:
- Color palettes: Experiment with complementary, analogous, or monochromatic
- Composition: Rule of thirds, symmetry, chaos
- Movement: Static, animated, interactive

**Creative Process**:
1. Choose algorithm that resonates
2. Experiment with parameters
3. Iterate based on aesthetic preference
4. Combine techniques for unique results

No single "correct" approach - let creativity guide you.
```

**Key Characteristics**:
- ✓ Multiple valid approaches presented
- ✓ Trade-offs explained
- ✓ Evaluation criteria provided
- ✓ Encourages experimentation
- ✗ No prescribed sequence
- ✗ No single "right" answer

---

### Medium Freedom (Recommended Pattern)

**When to Use**:
- Standard tasks with established best practices
- Workflows where some flexibility is beneficial
- Configuration decisions with recommended defaults
- Integration tasks with common patterns

**Guidance Style**:
- Recommend primary approach
- Provide 1-2 alternatives
- Explain when to deviate
- Allow configuration options

**Example: Setting Up Authentication**

```markdown
## Implementing Authentication

**Recommended Approach**: JWT-based stateless authentication

### Step 1: Choose JWT Algorithm

**Recommended**: HS256 (HMAC with SHA-256)
- Symmetric key, simpler setup
- Sufficient for single-server deployments

**Alternative**: RS256 (RSA with SHA-256)
- Asymmetric key, more complex
- Better for distributed systems
- Use when: Multiple services need to verify tokens

### Step 2: Configure Token Expiry

**Recommended**:
```python
ACCESS_TOKEN_EXPIRY = 15 * 60  # 15 minutes
REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 * 60  # 7 days
```

**Customize based on**:
- Security requirements (shorter = more secure)
- User experience (longer = less re-auth)
- Mobile vs web (mobile can use longer)

### Step 3: Implement Refresh Token Rotation

**Recommended Pattern**:
```python
def refresh_access_token(refresh_token):
    # Validate refresh token
    # Issue new access token
    # Issue new refresh token (rotation)
    # Invalidate old refresh token
    return new_access_token, new_refresh_token
```

**Why rotation**: Prevents refresh token theft from being permanent

### Step 4: Store Secrets Securely

**Required**:
- Never hardcode secrets in code
- Use environment variables or secret management

**Recommended**: Environment variables for development, Secret manager for production
```bash
export JWT_SECRET_KEY=$(openssl rand -base64 32)
```

**Production**: Use AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault
```

**Example: Database Connection Pooling**

```markdown
## Configuring Connection Pool

**Recommended Configuration**:
```python
pool_config = {
    'min_connections': 2,
    'max_connections': 10,
    'max_idle_time': 300,  # 5 minutes
    'max_lifetime': 3600,  # 1 hour
}
```

**Adjust based on**:

**Higher max_connections if**:
- High concurrent request volume
- Long-running queries
- Multiple services

**Lower max_connections if**:
- Database connection limit concerns
- Low traffic application
- Resource-constrained environment

**Rule of thumb**: `max_connections = (CPU cores * 2) + effective_spindle_count`

**Monitor and tune**:
- Watch connection wait times
- Track connection utilization
- Adjust based on production metrics
```

**Key Characteristics**:
- ✓ Clear recommended approach
- ✓ 1-2 viable alternatives
- ✓ Decision criteria for alternatives
- ✓ Configuration flexibility
- ✓ When to customize guidance
- ✗ Not mandatory sequence (but recommended)

---

### Low Freedom (Exact Sequence)

**When to Use**:
- Critical operations with severe error consequences
- Security-sensitive workflows
- Data integrity requirements
- Operations that can cause system lockout
- Compliance-required procedures

**Guidance Style**:
- Exact step-by-step sequence
- Explicit warnings for risks
- Validation at each step
- No deviation allowed

**Example: Production Deployment**

```markdown
## Deploying to Production

⚠️ CRITICAL: Follow exact order to avoid outages

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Code review approved
- [ ] Database migrations tested in staging
- [ ] Rollback plan documented

### Deployment Sequence

### Step 1: Create Backup

**FIRST - Before any changes**:
```bash
./backup.sh production
```

**Verify backup created**:
```bash
ls -lh backups/ | tail -1
```

Expected: Backup file with current timestamp

**DO NOT PROCEED if backup fails**

### Step 2: Enable Maintenance Mode

```bash
./maintenance-mode.sh on
```

**Verify**:
```bash
curl https://yourapp.com
```

Expected: Maintenance page displayed

### Step 3: Run Database Migrations

```bash
./migrate.sh production
```

**Verify each migration**:
```bash
./check-migrations.sh
```

Expected: All migrations applied successfully

**If migration fails**: Immediately run `./rollback.sh` and investigate

### Step 4: Deploy New Version

```bash
./deploy.sh production v2.0.0
```

**Wait for deployment completion** (do not interrupt)

### Step 5: Health Check

```bash
./health-check.sh --thorough
```

**Required checks**:
- [ ] Application responding (HTTP 200)
- [ ] Database connectivity
- [ ] External API connections
- [ ] Critical workflows functional

**If ANY check fails**: Execute rollback immediately

### Step 6: Monitor for 5 Minutes

```bash
./monitor.sh --duration=5m --alerts=critical
```

**Watch for**:
- Error rate spikes
- Response time increases
- Database connection errors
- User-reported issues

### Step 7: Disable Maintenance Mode

**ONLY if all checks passed**:
```bash
./maintenance-mode.sh off
```

### Step 8: Continue Monitoring

Monitor for 30 minutes after deployment:
- Check error logs every 5 minutes
- Monitor user activity metrics
- Be ready to rollback if issues emerge

## Rollback Procedure

**If ANY issue detected**:

```bash
# Immediate rollback
./rollback.sh production

# Verify rollback successful
./health-check.sh

# Re-enable site
./maintenance-mode.sh off

# Post-rollback
# 1. Document what failed
# 2. Fix issue in staging
# 3. Re-test thoroughly
# 4. Schedule new deployment
```

⚠️ **NEVER**:
- Skip backup step
- Deploy without testing migrations
- Proceed if health checks fail
- Disable monitoring
- Deploy during peak traffic hours
```

**Example: SSH Server Hardening**

```markdown
## Hardening SSH Configuration

⚠️ CRITICAL: Exact sequence required to avoid lockout

### Pre-Flight Safety Checklist
- [ ] Backup SSH access method exists
- [ ] Tested backup access in separate session
- [ ] Have physical/console access if needed
- [ ] Backup of current SSH config created

### Step 1: Verify Current Access

**In current terminal session**:
```bash
ssh user@server 'echo "Access confirmed"'
```

Expected: "Access confirmed" displayed

**DO NOT PROCEED if current access fails**

### Step 2: Create Backup SSH Key

```bash
ssh-keygen -t ed25519 -f ~/.ssh/backup_key_$(date +%Y%m%d)
```

### Step 3: Add Backup Key to Server

```bash
ssh-copy-id -i ~/.ssh/backup_key_$(date +%Y%m%d) user@server
```

### Step 4: Test Backup Key

**CRITICAL: Open NEW terminal session**:
```bash
ssh -i ~/.ssh/backup_key_$(date +%Y%m%d) user@server
```

**Verify**:
- [ ] Successfully connected
- [ ] Can execute sudo commands
- [ ] Keep this session OPEN

**DO NOT PROCEED unless backup access works**

### Step 5: Backup Current SSH Config

**In original session**:
```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup.$(date +%Y%m%d)
```

### Step 6: Modify SSH Config

**Edit /etc/ssh/sshd_config**:
```bash
sudo nano /etc/ssh/sshd_config
```

**Make these exact changes**:
```
# Disable password authentication
PasswordAuthentication no

# Disable root login
PermitRootLogin no

# Use SSH protocol 2 only
Protocol 2

# Change default port (optional but recommended)
Port 2222
```

### Step 7: Validate Config Syntax

```bash
sudo sshd -t
```

Expected: No errors

**If errors**: Fix before proceeding, DO NOT restart SSH

### Step 8: Restart SSH Service

⚠️ **KEEP BACKUP SESSION OPEN**

```bash
sudo systemctl restart sshd
```

### Step 9: Test New Configuration

**In THIRD terminal session**:
```bash
# If changed port
ssh -p 2222 user@server

# Otherwise
ssh user@server
```

**Verify**:
- [ ] Can connect with SSH key
- [ ] Cannot connect with password (try from different machine)
- [ ] Sudo access works

### Step 10: Verify All Sessions

**Required**:
- Original session: STILL CONNECTED
- Backup session: STILL CONNECTED
- New session: CONNECTED with new config

**If new session fails**:
1. Use backup session
2. Revert config: `sudo cp /etc/ssh/sshd_config.backup.$(date +%Y%m%d) /etc/ssh/sshd_config`
3. Restart SSH: `sudo systemctl restart sshd`
4. Investigate issue

### Step 11: Update Firewall (if port changed)

**ONLY if changed SSH port**:
```bash
sudo ufw allow 2222/tcp
sudo ufw delete allow 22/tcp
sudo ufw reload
```

**Test connection on new port before closing any sessions**

### Step 12: Close Original Sessions

**ONLY after confirming**:
- New config works
- New sessions can connect
- Backup access functional

Can now safely close original and backup sessions.
```

**Example: Database Migration with Rollback**

```markdown
## Running Database Migration

⚠️ CRITICAL: Data integrity at stake - exact sequence required

### Step 1: Backup Database

**MANDATORY first step**:
```bash
pg_dump -h localhost -U postgres -F c -b \
  -f backups/pre_migration_$(date +%Y%m%d_%H%M%S).backup \
  production_db
```

**Verify backup integrity**:
```bash
pg_restore --list backups/pre_migration_*.backup | head -20
```

Expected: Table of contents displayed

**Record backup details**:
```bash
echo "Migration backup: $(date), $(du -h backups/pre_migration_*.backup)" \
  >> migration.log
```

### Step 2: Test Migration in Dev Environment

```bash
# Restore prod backup to dev
pg_restore -d dev_db backups/pre_migration_*.backup

# Run migration on dev
./migrate.sh dev

# Verify dev data integrity
./verify-data.sh dev_db
```

**DO NOT proceed to production if dev migration fails**

### Step 3: Set Application to Read-Only Mode

```bash
./readonly-mode.sh on
```

**Verify no writes occurring**:
```bash
./check-db-activity.sh
```

Expected: No INSERT/UPDATE/DELETE operations

### Step 4: Create Database Checkpoint

```sql
CHECKPOINT;
SELECT pg_current_wal_lsn();
```

**Record WAL position** in migration.log for rollback reference

### Step 5: Run Migration

```bash
./migrate.sh production
```

**Do not interrupt** - let it complete

### Step 6: Verify Migration Success

```bash
# Check migration table
./check-migrations.sh

# Verify data integrity
./verify-data.sh production_db

# Run smoke tests
./smoke-tests.sh production_db
```

**Required checks**:
- [ ] All migrations marked as applied
- [ ] Row counts match expected
- [ ] Foreign key constraints valid
- [ ] Indexes created successfully
- [ ] Smoke tests pass

### Step 7: Decision Point

**If ALL verifications passed**:
- Proceed to Step 8

**If ANY verification failed**:
- Execute rollback procedure immediately
- DO NOT re-enable writes

### Step 8: Re-enable Writes

**ONLY if all verifications passed**:
```bash
./readonly-mode.sh off
```

### Step 9: Monitor Database

```bash
./monitor-db.sh --duration=10m
```

**Watch for**:
- Query errors
- Constraint violations
- Performance degradation
- Application errors

## Rollback Procedure

**Execute if migration or verification fails**:

```bash
# 1. Ensure read-only mode ON
./readonly-mode.sh on

# 2. Drop new tables/columns (if migration partial)
psql -d production_db -f rollback/drop_new_objects.sql

# 3. Restore from backup
pg_restore -d production_db backups/pre_migration_*.backup

# 4. Verify restore
./verify-data.sh production_db

# 5. Re-enable application (rollback complete)
./readonly-mode.sh off

# 6. Document failure
echo "Rollback completed: $(date), Reason: [FILL IN]" >> migration.log
```
```

**Key Characteristics**:
- ✓ Exact step-by-step sequence
- ✓ Explicit warnings before critical steps
- ✓ Validation after each step
- ✓ Clear "DO NOT PROCEED" instructions
- ✓ Rollback procedures documented
- ✓ Safety verifications required
- ✗ NO flexibility in sequence
- ✗ NO shortcuts allowed

---

## Choosing the Right Freedom Level

### Decision Matrix

| Criteria | High Freedom | Medium Freedom | Low Freedom |
|----------|-------------|----------------|-------------|
| **Error Impact** | Low | Medium | High/Critical |
| **Reversibility** | Easy to undo | Some effort to undo | Difficult/impossible |
| **Data at Risk** | None | Non-critical | Critical data |
| **Security Impact** | None | Minor | Major |
| **User Expertise** | Can vary | Intermediate+ | Any level |
| **Correct Approaches** | Many valid | Few preferred | One correct |
| **Compliance Required** | No | Sometimes | Yes |

### Examples by Domain

**High Freedom Domains**:
- Creative design (UI/UX, art, content)
- Architecture planning (initial phases)
- Prototyping and experimentation
- Research and exploration
- Algorithm selection for non-critical tasks

**Medium Freedom Domains**:
- Standard CRUD operations
- API integration (established protocols)
- Configuration management
- Testing strategies
- Code organization patterns

**Low Freedom Domains**:
- Security hardening
- Production deployments
- Database migrations
- Backup and restore
- System access management
- Compliance procedures
- Data deletion (GDPR, etc.)

### Red Flags Requiring Low Freedom

⚠️ **Use low freedom (exact sequence) if**:
- Mistake could lock you out (SSH, admin access)
- Data could be lost or corrupted (database operations)
- Security could be compromised (credential management)
- System could go down (production deployments)
- Compliance violation possible (regulated data handling)
- Irreversible consequences (data deletion, account termination)

### Signs Medium Freedom Is Appropriate

✓ **Use medium freedom (recommended pattern) if**:
- Best practices exist but alternatives work
- Configuration has common defaults
- Multiple tools solve the same problem
- User preference matters
- Environment differences require flexibility

### Indicators for High Freedom

✅ **Use high freedom (creative exploration) if**:
- Multiple solutions equally valid
- Creativity improves outcome
- Experimentation is safe
- Learning by doing is valuable
- No critical constraints

---

## Applying to Skill Workflows

### High Freedom Skill Example

```markdown
---
name: designing-ui
description: Create user interface designs exploring various approaches and styles. Use when designing UI without strict brand guidelines or constraints.
---

# UI Design Exploration

## Workflow

Explore design approaches:
1. Research inspiration (competitor analysis, design galleries)
2. Sketch multiple concepts (divergent thinking)
3. Choose promising directions
4. Create high-fidelity mockups
5. Iterate based on feedback

**Creative freedom**: Experiment with layouts, colors, typography
**Constraints**: Accessibility standards (WCAG 2.1 AA minimum)
```

### Medium Freedom Skill Example

```markdown
---
name: setting-up-ci
description: Configure CI/CD pipeline following recommended patterns. Use when setting up automated testing and deployment workflows.
---

# CI/CD Pipeline Setup

## Workflow

**Recommended**: GitHub Actions with standard workflow

### Step 1: Create Workflow File

```yaml
# .github/workflows/ci.yml (recommended structure)
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
```

**Alternatives**: CircleCI, GitLab CI, Jenkins (use if already in ecosystem)

### Step 2: Configure Test Coverage

**Recommended**: 80% coverage threshold
**Adjust based on**: Project maturity, team size, risk tolerance
```

### Low Freedom Skill Example

```markdown
---
name: managing-production-secrets
description: Securely manage production secrets and credentials. Use when handling sensitive data in production environments with exact security protocols.
---

# Production Secrets Management

## Workflow

⚠️ CRITICAL: Follow exact sequence for security

### Step 1: Never Commit Secrets

**MANDATORY check before ANY commit**:
```bash
git diff --cached | grep -i "password\|secret\|api.key"
```

If matches found: Remove secrets, use environment variables

### Step 2: Use Secret Management Service

**Required for production**:
- AWS Secrets Manager, OR
- Azure Key Vault, OR
- HashiCorp Vault

**NOT acceptable**: .env files in production, hardcoded values

### Step 3: Rotate Secrets

**Required schedule**: Every 90 days minimum
**Process**: Create new → Deploy → Test → Revoke old → Verify

[Exact rotation steps with no flexibility]
```

---

## Summary

### Key Principles

1. **Match freedom to risk**: Higher risk = Lower freedom
2. **Default to medium**: When in doubt, provide recommended path with alternatives
3. **Be explicit**: State the freedom level in the workflow
4. **Explain why**: Tell users why this level of guidance is appropriate
5. **Provide escape hatches**: Even low freedom should have emergency procedures

### Application in Skills

```markdown
# In your SKILL.md

## Workflow: [Task Name]

**Freedom Level**: [High/Medium/Low]
**Why**: [Brief explanation of risk/flexibility]

[Then provide appropriate level of guidance]
```

### Quick Reference

- **High**: "Consider these approaches..." (exploration)
- **Medium**: "Recommended approach..." (with alternatives)
- **Low**: "⚠️ CRITICAL: Follow exact sequence..." (safety-critical)
