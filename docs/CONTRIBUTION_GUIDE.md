# AgentSpec Contribution Guide

> How to contribute new agents, commands, and KB domains to AgentSpec

---

## Before You Start

### Prerequisites

- [ ] Understand the 5-phase SDD workflow (brainstorm → define → design → build → ship)
- [ ] Read CLAUDE.md (development instructions)
- [ ] Understand agent tier system (T1, T2, T3)
- [ ] Know the KB-first resolution pattern

### Contribution Types

| Type | Effort | When |
|------|--------|------|
| New Capability (in existing agent) | 1-2 hours | Agent needs more features |
| New Agent | 4-6 hours | Domain needs specialist |
| New KB Domain | 3-4 hours | Need new knowledge area |
| Bug Fix | 1 hour | Found issue or improvement |
| Documentation | 1-2 hours | Clarify existing content |

---

## Creating a New Agent

### Step 1: Pre-Flight Checklist

Before writing code, verify:

- [ ] **No existing agent** does >60% of what you need? (Check `.claude/agents/README.md`)
- [ ] **Name is unique?** (Search `.claude/agents/*/` for name)
- [ ] **Domain is clear?** (Odoo specialist? Python developer? SQL optimizer?)
- [ ] **Tier is right?** (T1 for utility, T2 for expert, T3 for platform specialist)
- [ ] **3+ trigger scenarios** exist? (Different reasons to use this agent)
- [ ] **KB domain available?** (Or create one)

If ANY box is unchecked, reconsider or create separate agent.

### Step 2: Gather Requirements

Ask yourself:

```markdown
## Agent Requirements

**Name:** {agent-name}
**Tier:** T1 / T2 / T3
**Domain:** {primary domain}
**Purpose:** {one-sentence mission}

**Trigger Scenarios:**
1. {User asks for A}
2. {User does B}
3. {User needs C}

**Capabilities:**
1. {What can it do?}
2. {What can it do?}
3. {What can it do?}

**Scale:** Lines of code estimate
- T1: 80-150 lines
- T2: 150-350 lines
- T3: 350-600 lines

**KB Domains Needed:**
- domain1
- domain2
```

### Step 3: Create Agent File

**Location:** `.claude/agents/{category}/{agent-name}.md`

**Template:** Use `.claude/agents/_template.md` as base

**Sections Required:**

For **T1 (Utility):**
- Identity + Domain + Threshold
- Knowledge Resolution
- Capability 1
- Constraints
- Quality Gate
- Response Format

For **T2+ (Expert/Specialist):**
- All of T1, plus:
- Capabilities 2-4 (more detail)
- Confidence Matrix
- Agreement Matrix
- Stop Conditions
- Escalation Rules
- Anti-patterns

For **T3 (Platform Specialist):**
- All of T2, plus:
- Knowledge Sources (detailed)
- Context Decision Tree
- MCP Server definitions

### Step 4: Code Review

Create GitHub issue: `[NEW AGENT] {agent-name}`

```markdown
---
name: Create New Agent
about: Proposal for a new specialized agent
---

**Agent Name:** {agent-name}
**Tier:** T1/T2/T3
**Domains:** [list]

**4 Trigger Examples:**
1. User: "..."  Agent: "I'll use..."
2. ...

**PR:** Will create when blueprint approved
```

Wait for feedback before PRing the file.

### Step 5: Create Pull Request

```bash
git checkout -b feat/new-agent-{name}
cp .claude/agents/_template.md .claude/agents/{category}/{agent-name}.md

# Fill in the template with your agent definition

git add .claude/agents/{category}/{agent-name}.md
git commit -m "feat: add $agent-name specialist agent

- Tier: T{N}
- Domains: [list]
- Triggers: [list]

Closes #{issue-number}"

git push origin feat/new-agent-{name}
```

### Step 6: PR Checklist

Before merging:

- [ ] Frontmatter is valid YAML
- [ ] All required sections present (based on tier)
- [ ] Confidence scoring matrix complete
- [ ] Escalation rules are specific
- [ ] Anti-patterns are actionable
- [ ] Examples are real/plausible
- [ ] Response format matches style
- [ ] GitHub Actions validator passes
- [ ] Code review approved

---

## Creating a New KB Domain

### Step 1: Identify Knowledge Area

```markdown
**Domain Name:** {descriptive-name}
**Purpose:** What does this domain teach?
**Agent Users:** Which agents will reference this?
**Size:** Small (3-5 concepts), Medium (6-8), Large (10+)
```

Examples:
- `odoo` — Odoo ERP 14-17 knowledge
- `dbt` — dbt development patterns
- `spark` — PySpark, Spark SQL

### Step 2: Create Domain Structure

```bash
mkdir -p .claude/kb/{domain-name}/concepts
mkdir -p .claude/kb/{domain-name}/patterns
touch .claude/kb/{domain-name}/index.md
touch .claude/kb/{domain-name}/quick-reference.md
```

### Step 3: Create Core Files

**index.md** (150-300 lines)
```markdown
# {Domain} Knowledge Base

Overview of the domain with topic headings.

## Topics

- Topic 1 (see concepts/file1.md)
- Topic 2 (see concepts/file2.md)
- ...

## Quick Links

- [Concepts](./concepts/) — Theory (N files)
- [Patterns](./patterns/) — Working code (N files)
- [Quick Reference](./quick-reference.md)
```

**quick-reference.md** (100-200 lines)
```markdown
# {Domain} Quick Reference

Decision matrices, cheat sheet, version table, etc.

## Version Matrix

| Feature | v1 | v2 | v3 |
|---------|-----|-----|-----|
| ... | ... | ... | ... |

## Common Errors

| Error | Fix |
|-------|-----|
| ... | ... |
```

**concepts/*.md files** (3-6 files, 150-300 lines each)
```markdown
# Concept Name

Explain the concept.

## Key Points

- Point 1
- Point 2

## How to use

```python
# Code example
```
```

**patterns/*.md files** (3-6 files, 200-400 lines each)
```markdown
# Pattern Name

Real-world usage example.

## When to use

Describe scenario.

## Implementation

```python
# Complete, working code example
```

## Results

What you get.

## Common mistakes

Avoid X, do Y instead.
```

### Step 4: Create PR with Full Domain

```bash
git checkout -b feat/kb-{domain-name}

# Create all 12 files as described above

git add .claude/kb/{domain-name}/
git commit -m "feat: add {domain} KB domain

- index.md: Overview
- quick-reference.md: Decision matrices
- concepts/ (N files): Theory
- patterns/ (N files): Working examples

Closes #{issue-number}"

git push origin feat/kb-{domain-name}
```

### Step 5: Link to Agent

Update relevant agents to reference new KB domain:

```yaml
kb_domains: [..., {domain-name}]
```

Commit separately:
```bash
git commit -m "ref: link agents to {domain} KB domain"
```

---

## Creating a New Command

### Step 1: Design Command

```markdown
**Command Name:** /my-command
**Purpose:** What does user type this for?
**Input:** What does user provide?
**Output:** What does command do?
**Agent Delegation:** Which agent handles it?

## Usage Example

```bash
/my-command [arguments]
```

## What Happens

1. Parses input
2. Calls agent
3. Agent returns solution
4. Command presents result to user
```

### Step 2: Create Command File

**Location:** `.claude/commands/{category}/{command-name}.md`

**Sections:**
- Command name + description
- Usage
- Examples
- Overview (short + references)
- What this command does
- Process (steps or flowchart)
- Output
- Quality gate
- Tips
- References

### Step 3: Create PR

```bash
git checkout -b feat/command-{name}
# Create command file
git commit -m "feat: add /{command-name} command

- Delegates to: {agent}
- Purpose: {brief}

Closes #{issue-number}"

git push
```

---

## General Contributing Guidelines

### Code Quality

- [ ] Follow existing patterns
- [ ] Use consistent formatting
- [ ] Add examples that work
- [ ] Remove TODO comments before merge

### Testing

- [ ] Test agent locally in Claude Code
- [ ] Verify KB domain loads (`/design` references it)
- [ ] Test command with sample data
- [ ] No hardcoded paths (use `${CLAUDE_PLUGIN_ROOT}`)

### Documentation

- [ ] Write clear frontmatter
- [ ] Add working code examples
- [ ] Explain "why", not just "what"
- [ ] Link related domains/agents

### Git Workflow

```bash
# 1. Create feature branch
git checkout -b feat/your-feature

# 2. Make changes
# 3. Commit with clear message
git commit -m "feat: add X

- What was added
- Why it was needed

Closes #123"

# 4. Push
git push origin feat/your-feature

# 5. Create PR with template
# → Fill in all sections
# → Reference issue

# 6. Wait for review
# → Address feedback
# → Recommit (don't amend)

# 7. Merge when approved
```

---

## Contribution Checklist

### Before PR:

- [ ] Feature branch created from `develop`
- [ ] All files created/updated
- [ ] GitHub Actions workflow passes
- [ ] No TODOs left
- [ ] Examples are real
- [ ] Tested locally

### PR Body Filled:

- [ ] Title: `feat/fix/docs: ...`
- [ ] Description: What & Why
- [ ] Type marked: New agent/KB/command
- [ ] Related issue linked
- [ ] Testing procedure documented

### After Approval:

- [ ] Rebase on `develop`
- [ ] All conversations resolved
- [ ] Final check: works as documented
- [ ] Merge to `develop`
- [ ] Close linked issue

---

## Questions? Issues?

- **Compare with existing:** Check `.claude/agents/README.md` for routing
- **Ask in issue:** Create `[QUESTION]` issue for guidance
- **Review examples:** Look at `dbt-specialist` or `schema-designer` agents
- **Check tests:** Run `/build` on a DESIGN document

---

**Welcome to AgentSpec! 🚀**

Every new agent, KB domain, and command makes the system stronger.

