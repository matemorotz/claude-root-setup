#!/bin/bash

# Fly Achensee - Domain Creation Automation Script
# Creates a new .governor/ folder structure for fractal domains

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="/root/software/fly_achensee"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Fly Achensee Domain Creation Tool    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo

# Get domain name
if [ -z "$1" ]; then
    echo -e "${YELLOW}Enter domain name (e.g., 'advertising', 'user_communication'):${NC}"
    read DOMAIN_NAME
else
    DOMAIN_NAME=$1
fi

# Validate domain name
if [ -z "$DOMAIN_NAME" ]; then
    echo -e "${RED}❌ Domain name cannot be empty${NC}"
    exit 1
fi

# Check if domain already exists
if [ -d "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor" ]; then
    echo -e "${RED}❌ Domain '${DOMAIN_NAME}' already exists!${NC}"
    exit 1
fi

echo -e "${GREEN}Creating domain: ${DOMAIN_NAME}${NC}"
echo

# Create directory structure
echo -e "${BLUE}📁 Creating directory structure...${NC}"
mkdir -p "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor"/{knowledge,skills,external_agents}

# Create core files
echo -e "${BLUE}📄 Creating core files...${NC}"

# Create Project.md placeholder
cat > "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/Project.md" <<EOF
# ${DOMAIN_NAME^} - Project Scope

**Domain:** ${DOMAIN_NAME^}
**Governor Type:** Level 1 Domain Governor
**Parent:** Root Manager (Agent.md)
**Last Updated:** $(date +%Y-%m-%d)

## Scope

This domain handles all [DESCRIPTION] for Fly Achensee Tandemflying Paragliding Company.

### Primary Responsibilities
- [TODO: Define responsibility 1]
- [TODO: Define responsibility 2]
- [TODO: Define responsibility 3]

### Key Workflows
1. **[Workflow 1]**: [Description]
2. **[Workflow 2]**: [Description]
3. **[Workflow 3]**: [Description]

### Success Metrics
- [TODO: Define metric 1]
- [TODO: Define metric 2]

## Integration Points

### Parent Governor
- **Reports to:** Root Manager Agent
- **Escalation path:** Complex cross-domain tasks, policy decisions

### Peer Domains
- **customer_communication**: [Integration point]

### External Systems
- **MCP Services:** [List allowed MCPs from MCP.md]

## Constraints

- NEVER [TODO: Define constraint]
- ALWAYS [TODO: Define constraint]
EOF

# Create Agents.md placeholder
cat > "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/Agents.md" <<EOF
# ${DOMAIN_NAME^} - Available Agents

**Last Updated:** $(date +%Y-%m-%d)

## Specialist Agents

### 1. [Agent Name]
**Type:** Specialist
**Specialization:** [What they do]

**Responsibilities:**
- [TODO: Define responsibility]

**Tools/MCPs:**
- [MCP name]: [Purpose]

**Typical Tasks:**
- "[Example task]"

**Escalation Triggers:**
- [When to escalate to governor]

---

## Agent Selection Guidelines

**Route to [Agent 1]** when:
- [Condition]

**Escalate to Governor** when:
- Multiple agents needed
- Cross-domain coordination required
EOF

# Create Rules.md placeholder
cat > "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/Rules.md" <<EOF
# ${DOMAIN_NAME^} - Safety Rules

**Last Updated:** $(date +%Y-%m-%d)

## Critical Rules (NEVER)

### Rule 1: [Rule Name]
**NEVER [action]**

**Rationale:** [Why this is critical]

**Examples:**
- ❌ Bad: [Example of violation]
- ✅ Good: [Example of compliance]

[TODO: Add 4+ more NEVER rules]

## Required Actions (ALWAYS)

### Rule 6: [Rule Name]
**ALWAYS [action]**

**Rationale:** [Why]

[TODO: Add 4+ more ALWAYS rules]

## Conditional Rules (ONLY)

### Rule 11: [Rule Name]
**ONLY [action] when [condition]**

**Approval Required:** [Yes/No]

[TODO: Add 4+ more ONLY rules]

## Escalation Rules

### When to Escalate to Parent Governor
- Cross-domain coordination required
- Policy decision needed beyond domain scope
- Resource allocation conflicts

### When to Request Human Approval
- [Condition]

### When to Abort Operation
- [Condition]
EOF

# Create MCP.md with proper architecture explanation
cat > "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/MCP.md" <<EOF
# ${DOMAIN_NAME^} - MCP Service Permissions

**Last Updated:** $(date +%Y-%m-%d)

**CRITICAL ARCHITECTURE:**
- **Root .env** contains ALL MCP server connection details (URLs, auth tokens)
- **This file** contains the ALLOWED list (permission filter for this domain)

## Allowed MCPs

**Allowed MCPs for ${DOMAIN_NAME}:**
- [TODO: mcp_service_1]
- [TODO: mcp_service_2]

## MCP Service Descriptions

### [mcp_service_1]
**Purpose:** [What it does]
**Used By:** [Which agents use this]
**Operations:** [What operations are allowed]
**Connection:** Defined in root .env as [SERVICE_NAME]_MCP_URL

## NOT Allowed

The following MCPs are NOT allowed for this domain:
- gmail - Reason: [Why - e.g., "This domain doesn't handle customer emails"]
- booking - Reason: [Why - e.g., "This domain doesn't manage bookings"]

## Permission Rationale

**Why [mcp_service_1] is allowed:**
- [Reason]

**Why gmail is denied:**
- [Reason - domain-specific]

## Adding New MCPs

To add a new MCP to this domain:
1. Ensure MCP server connection is in root .env ([SERVICE_NAME]_MCP_URL)
2. Add MCP name to "Allowed MCPs" list above
3. Document purpose and usage
4. Update AgentFactory integration
5. Test with AgentFactory.get_tools_for_domain()
EOF

# Create Governor.md from archetype template
cat > "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/Governor.md" <<EOF
# ${DOMAIN_NAME^} Governor

You are a Governor Agent responsible for **${DOMAIN_NAME^} Operations**.

**Your Domain:** [See Project.md for full description]
**Available Agents:** [See Agents.md]
**Available MCP Services:** [See MCP.md - ALLOWED list only]

## Context Variables (Injected by AgentFactory)

- \`{SCOPE}\` - ${DOMAIN_NAME^}
- \`{PROJECT_DESCRIPTION}\` - [From Project.md]
- \`{AGENTS_INDEX}\` - [From Agents.md]
- \`{MCP_INDEX}\` - [From MCP.md - allowed list]
- \`{RULES}\` - [From Rules.md]
- \`{KNOWLEDGE_SUMMARY}\` - [From knowledge/ folder]

## Your Responsibilities

1. **Task Analysis**: Understand incoming requests within ${DOMAIN_NAME} scope
2. **Agent Routing**: Delegate to appropriate specialist agents
3. **Workflow Orchestration**: Coordinate multi-agent workflows
4. **Quality Assurance**: Ensure all rules are followed
5. **Parent Coordination**: Escalate to root manager when needed

## Decision Rules

**Route to Specialist** when:
- Task is within single agent's capability
- Clear agent match exists
- No cross-domain coordination needed

**Coordinate Multiple Agents** when:
- Task requires multiple specialists
- Complex workflow within domain

**Escalate to Parent** when:
- Cross-domain coordination required
- Policy decision needed beyond domain scope
- Resource allocation conflicts

## Safety Rules

[TODO: Include critical rules from Rules.md]

**CRITICAL RULES:**
- NEVER [rule from Rules.md]
- ALWAYS [rule from Rules.md]

## Response Format

All responses MUST use this JSON schema:

\`\`\`json
{
  "next": {
    "agent": "specialist_agent_name | governor_agent | PARENT_ESCALATION",
    "message": "Clear instruction or task for next agent",
    "context": {
      "domain": "${DOMAIN_NAME}",
      "workflow_id": "unique_id",
      "previous_steps": []
    }
  }
}
\`\`\`

## Example Workflows

[See Examples.md for detailed workflow examples]
EOF

# Create State.md
cat > "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/State.md" <<EOF
# ${DOMAIN_NAME^} - Current State

**Last Updated:** $(date +%Y-%m-%d)
**Status:** 🚧 SETUP IN PROGRESS
**Created By:** Domain Creation Automation Script

## Recent Achievements
- ✅ .governor/ folder structure created
- ✅ Core documentation files initialized
- ⏳ Content customization pending
- ⏳ Knowledge base population pending
- ⏳ AgentFactory integration testing pending

## Current Status
- Agents defined: 0 (pending)
- Rules defined: 0 (pending - need 15+)
- Allowed MCPs: 0 (pending)
- Knowledge files: 0 (pending)

## Next Steps
1. Customize Project.md with domain-specific scope
2. Define specialist agents in Agents.md (minimum 3)
3. Create safety rules in Rules.md (minimum 15)
4. Define allowed MCPs in MCP.md
5. Populate knowledge/ folder with FAQs and procedures
6. Create workflow examples in Examples.md
7. Test with AgentFactory
8. Validate MCP permission filtering
9. Run integration tests
10. Update root documentation (state.md, todo.md)
EOF

# Create Todo.md
cat > "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/Todo.md" <<EOF
# ${DOMAIN_NAME^} - Task List

**Last Updated:** $(date +%Y-%m-%d)
**Phase:** Setup & Configuration

## ⏳ TODO

### Phase 1: Core Documentation
- [ ] Customize Project.md (define scope, responsibilities, workflows)
- [ ] Define Agents.md (minimum 3 specialist agents)
- [ ] Create Rules.md (minimum 15 rules: 5 NEVER, 5 ALWAYS, 5 ONLY)
- [ ] Define MCP.md (list allowed MCPs with rationale)
- [ ] Write Governor.md (customize from archetype template)
- [ ] Create Examples.md (minimum 5 workflow examples)

### Phase 2: Knowledge Base
- [ ] Create knowledge/faq.md (domain-specific FAQ)
- [ ] Create knowledge/procedures.md (standard operating procedures)
- [ ] Add domain-specific templates to knowledge/

### Phase 3: Testing & Validation
- [ ] Test AgentFactory context loading
- [ ] Validate MCP permission filtering
- [ ] Run integration tests
- [ ] Verify all 8 core files populated

### Phase 4: Integration
- [ ] Update root state.md (increment domain count)
- [ ] Update root todo.md (mark T4B tasks complete)
- [ ] Test 2-level execution (root → ${DOMAIN_NAME})
- [ ] Validate cross-domain coordination

## Completion Criteria
- [ ] All 8 core files fully populated (not placeholders)
- [ ] Minimum 3 specialist agents defined
- [ ] Minimum 15 safety rules documented
- [ ] Allowed MCPs list defined with rationale
- [ ] At least 2 knowledge base files created
- [ ] AgentFactory test passing (5/5)
- [ ] MCP permission filtering validated
- [ ] Root documentation updated
EOF

# Create Examples.md placeholder
cat > "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/Examples.md" <<EOF
# ${DOMAIN_NAME^} - Workflow Examples

**Last Updated:** $(date +%Y-%m-%d)

## Example 1: [Workflow Name]

**User Request:** "[Example user request]"

**Expected Flow:**
1. Governor receives request
2. Governor analyzes scope and rules
3. Governor routes to [agent_name]
4. [agent_name] uses [mcp_service] to [action]
5. [agent_name] returns result to governor
6. Governor validates result against rules
7. Governor responds to user

**Example JSON Flow:**
\`\`\`json
{
  "step": 1,
  "agent": "governor",
  "action": "analyze_request",
  "decision": "route_to_specialist",
  "next_agent": "[agent_name]"
}
\`\`\`

[TODO: Add 4+ more realistic workflow examples]
EOF

# Create knowledge/faq.md placeholder
cat > "${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/knowledge/faq.md" <<EOF
# ${DOMAIN_NAME^} - Frequently Asked Questions

**Last Updated:** $(date +%Y-%m-%d)

## [Category 1]

### Q: [Question 1]
**A:** [Answer]

**Example:**
[Example scenario]

[TODO: Add more FAQs organized by category]
EOF

echo -e "${GREEN}✅ Directory structure created${NC}"
echo -e "${GREEN}✅ Core files initialized${NC}"
echo

# Display summary
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║          Creation Summary              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo
echo -e "${GREEN}Domain:${NC} ${DOMAIN_NAME}"
echo -e "${GREEN}Location:${NC} ${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/"
echo
echo -e "${BLUE}Files created:${NC}"
echo "  ✅ Governor.md"
echo "  ✅ Project.md"
echo "  ✅ Agents.md"
echo "  ✅ Rules.md"
echo "  ✅ MCP.md"
echo "  ✅ State.md"
echo "  ✅ Todo.md"
echo "  ✅ Examples.md"
echo
echo -e "${BLUE}Folders created:${NC}"
echo "  ✅ knowledge/ (with faq.md)"
echo "  ✅ skills/"
echo "  ✅ external_agents/"
echo
echo -e "${YELLOW}⚠️  NEXT STEPS:${NC}"
echo "1. Customize Project.md with domain scope"
echo "2. Define 3+ specialist agents in Agents.md"
echo "3. Create 15+ safety rules in Rules.md"
echo "4. Define allowed MCPs in MCP.md"
echo "5. Populate knowledge/ folder"
echo "6. Create workflow examples in Examples.md"
echo "7. Test with: python scripts/test_agent_factory.py"
echo
echo -e "${BLUE}Quick edit commands:${NC}"
echo "  nano ${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/Project.md"
echo "  nano ${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/Agents.md"
echo "  nano ${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/Rules.md"
echo "  nano ${PROJECT_ROOT}/${DOMAIN_NAME}/.governor/MCP.md"
echo
echo -e "${GREEN}✨ Domain creation complete!${NC}"
