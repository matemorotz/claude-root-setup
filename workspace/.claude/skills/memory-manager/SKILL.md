---
name: memory-manager
description: Manage and optimize all memory systems including CLAUDE.md, Skills, Memory API, and configuration files. Use when dealing with memory storage, context optimization, knowledge organization, or cross-system searches.
allowed-tools: Read, Write, Edit, Grep, Bash
---

# Memory Manager Skill

## Purpose
Unified interface for managing Claude's five complementary memory systems:
1. CLAUDE.md files (static context)
2. Skills (smart on-demand capabilities)
3. Memory (#) command (quick notes)
4. Custom Memory API (searchable history)
5. Slash Commands (user workflows)

## When to Use This Skill
- User mentions "memory", "remember", "store", "context"
- Need to decide where to store new information
- Searching across memory systems
- Optimizing context window usage
- Managing knowledge base
- Troubleshooting memory-related issues

## Core Capabilities

### 1. Memory Classification
Analyze information and recommend storage location:
- **CLAUDE.md**: Core rules, always-applicable patterns (<100 words)
- **Skill**: Complex workflows, conditional use (>500 words)
- **Memory (#)**: Quick reminders, temporary notes
- **Memory API**: Historical records, searchable context
- **Slash Command**: Repetitive prompt templates

### 2. Cross-System Search
Search all memory systems simultaneously:
```bash
# CLAUDE.md files
grep -r "search_term" /root/*.md ~/.claude/*.md

# Memory API
curl -H "Authorization: Menycibu" \
  http://localhost:8000/search \
  -d '{"query_text": "search_term", "max_results": 10}'

# Skills
grep -r "search_term" ~/.claude/skills/*/SKILL.md
```

### 3. Context Optimization
Check and optimize context window usage:
- CLAUDE.md size audit
- Skill activation patterns
- Memory (#) cleanup suggestions

### 4. Memory Migration
Move information between systems:
- Promote Memory (#) → CLAUDE.md (if recurring 3+ times)
- Convert repeated workflows → Skills
- Archive old reminders → Memory API

## Decision Framework

### Store in CLAUDE.md If:
✅ Applies to EVERY session
✅ Critical rule that must never be forgotten
✅ Project-wide convention
✅ Small (<100 words)
❌ NOT if: Large content, historical record, conditional use

### Create a Skill If:
✅ Complex multi-step workflow
✅ Only needed sometimes (conditional)
✅ Includes executable scripts
✅ Want Claude to auto-decide when to use
❌ NOT if: Always applicable, simple reminder

### Use Memory (#) If:
✅ Quick reminder (<50 words)
✅ Just learned something important
✅ Project-specific quirk
✅ Temporary note
❌ NOT if: Need to search later, complex workflow

### Store in Memory API If:
✅ Historical implementation record
✅ Decision rationale ("why we did X")
✅ Problem solution
✅ Need to search/filter later
❌ NOT if: Current rule, workflow, quick note

### Create Slash Command If:
✅ Repetitive prompt you type often
✅ Want arguments/templating
✅ User-triggered (not auto-invoked)
❌ NOT if: Want Claude to auto-trigger

## Common Operations

### Check Memory System Health
```bash
# CLAUDE.md size
wc -w /root/CLAUDE.md /root/CLAUDE_MASTER_RULES.md /root/project.md

# Skills count
ls ~/.claude/skills/ | wc -l

# Memory API status
curl -s -H "Authorization: Menycibu" http://localhost:8000/health
```

### Search Memory API
```bash
curl -H "Authorization: Menycibu" \
  -H "Content-Type: application/json" \
  http://localhost:8000/search \
  -d '{
    "query_text": "authentication",
    "project_filter": "api_system",
    "similarity_threshold": 0.3,
    "max_results": 10
  }'
```

### Store to Memory API
```bash
curl -H "Authorization: Menycibu" \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8000/message \
  -d '{
    "message": "Implemented JWT refresh token rotation",
    "context": {
      "user": "mate",
      "project": "auth_system",
      "priority": "high",
      "keywords": ["JWT", "security"]
    }
  }'
```

### Audit CLAUDE.md
```bash
# Check total size
cat /root/CLAUDE.md /root/CLAUDE_MASTER_RULES.md /root/project.md | wc -w

# Find outdated content
grep -n "TODO\|FIXME\|DEPRECATED" /root/*.md

# List Memory (#) additions
grep -A 2 "Quick Reminders" /root/CLAUDE.md
```

## Integration with MCP Tools

The memory-system MCP server provides these tools:
- `process_memory_message` - Create memory with metadata
- `search_memories` - Semantic search with filters
- `get_memory_by_id` - Retrieve specific memory
- `list_memories_by_user` - Filter by user
- `list_memories_by_project` - Filter by project

## Workflow Examples

### Example 1: New Information Arrives
```
User: "Always use async/await in this project"

Analysis:
- Applies to all sessions? YES
- Size: 6 words
- Type: Code convention

Decision: Add to CLAUDE.md (project.md section)
```

### Example 2: Complex Debugging Process
```
User: "Help debug MT5 connection issues"

Analysis:
- Multi-step process? YES
- Only needed sometimes? YES
- Includes commands? YES

Decision: Activate mt5-debug Skill (if exists) or create new skill
```

### Example 3: Implementation Record
```
User: "We tried Redis clustering but it caused latency issues, went with single instance"

Analysis:
- Historical context? YES
- Need to search later? YES
- Decision rationale? YES

Decision: Store in Memory API with metadata
```

## Maintenance Tasks

### Weekly Cleanup
1. Review Memory (#) entries >30 days
2. Archive to Memory API
3. Check CLAUDE.md size (<10,000 tokens)
4. Audit skill activation patterns

### Monthly Review
1. Promote recurring Memory (#) to CLAUDE.md
2. Update project.md with new patterns
3. Create skills for repeated workflows
4. Clean up outdated content

## Scripts Available

### scripts/search-all.sh
Search across all memory systems

### scripts/classify-memory.sh
Analyze information and suggest storage location

### scripts/migrate-memory.sh
Move information between systems

### scripts/audit-context.sh
Check context window usage

## Troubleshooting

### Memory API Not Responding
```bash
# Check if running
ps aux | grep memory_mcp_server

# Check health
curl -s http://localhost:8000/health

# Restart if needed
cd /root/memory_system && node memory_mcp_server.js &
```

### CLAUDE.md Too Large
1. Split into multiple @imported files
2. Move historical context to Memory API
3. Create skills for conditional content

### Skills Not Activating
1. Improve description with keywords
2. Make description more specific about "when to use"
3. Test with explicit mention

## Best Practices

1. **One Source of Truth**: Each piece of information lives in ONE system
2. **Progressive Disclosure**: Use skills for conditional content
3. **Regular Maintenance**: Weekly cleanup, monthly review
4. **Rich Metadata**: Always add context to Memory API entries
5. **Clear Descriptions**: Skills need good descriptions to activate

## Reference Documentation
- Knowledge Base: /root/docs/CLAUDE_CONFIG_KNOWLEDGE_BASE.md
- Improvement Plan: /root/docs/INTEGRATED_MEMORY_IMPROVEMENT_PLAN.md
- Memory API Guide: /root/MEMORY_QUICK_REFERENCE.md
