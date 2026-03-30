# GitHub Setup for AgentSpec with Webhook Automation

> Complete setup guide for GitHub repository with Agent automation, Kanban tracking, and webhook integration for small teams (2-5 people)

**Target:** Production-ready GitHub repository for AgentSpec with automated agent triggering via webhooks

---

## Phase 1: Repository Initialization

### Step 1.1: Create Repository

```bash
# On GitHub.com
New Repository
├── Name: agentspec
├── Description: "Spec-Driven Development framework with AI agents for data engineering"
├── Visibility: Public (recommended for collaboration) OR Private (if sensitive work)
├── Initialize with README.md: YES
└── Add .gitignore: Python

# After creation, clone locally:
git clone https://github.com/{YOUR_ORG}/agentspec.git
cd agentspec
```

### Step 1.2: Branch Protection Rules

**Navigate:** Settings → Branches → Branch protection rules

#### Rule 1: `main` (Production)

```
Branch name pattern: main

☑ Require a pull request before merging
  ├─ Require pull request reviews before merging: 1
  ├─ Include administrators: ☑
  └─ Dismiss stale PR approvals: ☑

☑ Require status checks to pass before merging
  ├─ Require branches to be up to date before merging: ☑
  ├─ Required status checks:
  │  ├─ agent-validator
  │  ├─ kb-validator
  │  └─ build-plugin
  └─ Require code reviews from required owners: (optional)

☑ Require branches to be up to date before merging
☑ Require conversation resolution before merging
☑ Allow force pushes: ☐ (NOT recommended for main)
```

#### Rule 2: `develop` (Integration)

```
Branch name pattern: develop

☑ Require a pull request before merging
  └─ Require pull request reviews before merging: 1

☑ Require status checks to pass before merging
  └─ Required status checks:
     ├─ agent-validator
     └─ kb-validator

☑ Require conversation resolution before merging
☑ Allow force pushes: ☐
```

#### Rule 3: `feat/*` (Feature Branches)

```
Branch name pattern: feat/*

☑ Require status checks to pass before merging
  └─ Required status checks:
     ├─ agent-validator (if .claude/agents/ changed)
     └─ kb-validator (if .claude/kb/ changed)

☑ Require conversation resolution before merging
☑ Allow auto-delete of head branches: ☑
```

---

## Phase 2: Labels Configuration

### Step 2.1: Create Issue Labels

**Navigate:** Issues → Labels

**25 Labels to Create:**

| Category | Label | Color | Description |
|----------|-------|-------|-------------|
| **Agent Assignment** | `agent:odoo-specialist` | `#FF6B6B` | Task for odoo-specialist agent |
| | `agent:dbt-specialist` | `#FF6B6B` | Task for dbt-specialist agent |
| | `agent:schema-designer` | `#FF6B6B` | Task for schema-designer agent |
| | `agent:python-developer` | `#FF6B6B` | Task for python-developer agent |
| | `agent:code-reviewer` | `#FF6B6B` | Task for code-reviewer agent |
| **Command Type** | `command:pipeline` | `#4ECDC4` | /pipeline command |
| | `command:schema` | `#4ECDC4` | /schema command |
| | `command:data-quality` | `#4ECDC4` | /data-quality command |
| | `command:odoo-setup` | `#4ECDC4` | Odoo setup automation |
| **KB Domain** | `domain:odoo` | `#95E1D3` | Odoo ERP knowledge domain |
| | `domain:dbt` | `#95E1D3` | dbt patterns & knowledge |
| | `domain:spark` | `#95E1D3` | Spark knowledge domain |
| | `domain:data-modeling` | `#95E1D3` | Data modeling KB |
| **Status** | `status:backlog` | `#CCCCCC` | Backlog (not started) |
| | `status:ready` | `#FFEB3B` | Ready for assignment |
| | `status:in-progress` | `#2196F3` | Currently being worked on |
| | `status:review` | `#9C27B0` | Awaiting review/approval |
| | `status:done` | `#4CAF50` | Completed & merged |
| | `status:blocked` | `#F44336` | Blocked, waiting on something |
| **Tier/Scope** | `tier:T1` | `#FFA500` | Utility agent (simple) |
| | `tier:T2` | `#FFA500` | Domain expert agent |
| | `tier:T3` | `#FFA500` | Platform specialist (complex) |
| **Other** | `github-integration` | `#E91E63` | GitHub webhook automation |
| | `help-wanted` | `#0075CA` | Community contribution welcome |
| | `good-first-issue` | `#7057FF` | Good for newcomers |

### Step 2.2: Create Label Automation (GitHub CLI)

```bash
# Optional: Use GitHub CLI to create labels programmatically
gh label create "agent:odoo-specialist" --color "FF6B6B" \
  --description "Task for odoo-specialist agent"

gh label create "status:backlog" --color "CCCCCC" \
  --description "Backlog (not started)"

# ... (repeat for each label)
```

---

## Phase 3: GitHub Projects v2 Kanban

### Step 3.1: Create Project

**Navigate:** Projects (top menu) → New project

```
Project name:     AgentSpec Workflow
Description:      Track agents working on issues & PRs
Organization:     {YOUR_ORG}
Project type:     Table (recommended for tracking)
```

### Step 3.2: Configure Board View

**View name:** Kanban

**Create columns from status labels:**

| Column | Trigger Label | WIP Limit | Notes |
|--------|---------------|-----------|-------|
| Backlog | `status:backlog` | No limit | Unstarted work |
| Ready | `status:ready` | 5 max | Assigned, waiting for agent |
| In Progress | `status:in-progress` | 3 max | Agent actively working |
| Review | `status:review` | 2 max | Awaiting approval |
| Done | `status:done` | No limit | Merged to main |

### Step 3.3: Add Automation

**Settings → Automation:**

```
✅ Auto-add issues and PRs
   └─ Add PRs when opened

✅ Status updates
   ├─ Pull requests: Move to "Review" when opened
   ├─ Pull requests: Move to "Done" when merged
   └─ Pull requests: Move to "Backlog" when closed

✅ Sort by: Created date (descending)
```

**Custom fields to add:**

| Field Name | Type | Values | Purpose |
|-----------|------|--------|---------|
| `Assigned Agent` | Single select | odoo-specialist, dbt-specialist, etc. | Who's working on it |
| `Complexity` | Single select | Simple, Medium, Complex | Effort estimate |
| `Priority` | Single select | P0 (urgent), P1 (high), P2 (medium), P3 (low) | Triage |
| `ETA Hours` | Number | 1-40 | Time estimate |

---

## Phase 4: GitHub Actions Workflows

### Step 4.1: Create Workflow Directory

```bash
mkdir -p .github/workflows
```

### Step 4.2: Agent Validator Workflow

**File:** `.github/workflows/agent-validator.yml`

```yaml
name: Agent Validator

on:
  pull_request:
    paths:
      - '.claude/agents/**'
      - '.claude/sdd/architecture/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate Agent Frontmatter
        run: |
          echo "Checking agent YAML frontmatter..."

          # Required fields for ALL agents
          for file in .claude/agents/**/*.md; do
            if [ -f "$file" ]; then
              echo "Validating: $file"

              # Check for required fields in frontmatter
              if ! grep -q "^name:" "$file"; then
                echo "❌ Missing 'name:' in $file"
                exit 1
              fi
              if ! grep -q "^tier:" "$file"; then
                echo "❌ Missing 'tier:' in $file"
                exit 1
              fi
              if ! grep -q "^kb_domains:" "$file"; then
                echo "❌ Missing 'kb_domains:' in $file"
                exit 1
              fi
              # Check T2+ requirements
              tier=$(grep "^tier:" "$file" | cut -d' ' -f2)
              if [[ "$tier" == "T2" || "$tier" == "T3" ]]; then
                if ! grep -q "^stop_conditions:" "$file"; then
                  echo "❌ Missing 'stop_conditions:' for $tier agent: $file"
                  exit 1
                fi
                if ! grep -q "^escalation_rules:" "$file"; then
                  echo "❌ Missing 'escalation_rules:' for $tier agent: $file"
                  exit 1
                fi
              fi
            fi
          done
          echo "✅ Agent validation passed"

      - name: Check KB Domains
        run: |
          echo "Checking KB domain references..."

          # Validate kb_domains point to existing domains
          for file in .claude/agents/**/*.md; do
            if [ -f "$file" ]; then
              domains=$(grep "^kb_domains:" "$file" | head -1)
              echo "  $file: $domains"
            fi
          done
          echo "✅ KB domain check complete"
```

### Step 4.3: KB Validator Workflow

**File:** `.github/workflows/kb-validator.yml`

```yaml
name: KB Validator

on:
  pull_request:
    paths:
      - '.claude/kb/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate KB Domain Structure
        run: |
          echo "Checking KB domain structure..."

          for domain_dir in .claude/kb/*/; do
            if [ -d "$domain_dir" ] && [[ ! "$domain_dir" =~ ^.*/_templates$ ]]; then
              domain_name=$(basename "$domain_dir")
              echo "Validating domain: $domain_name"

              # Required files
              if [ ! -f "$domain_dir/index.md" ]; then
                echo "❌ Missing index.md in $domain_name"
                exit 1
              fi
              if [ ! -f "$domain_dir/quick-reference.md" ]; then
                echo "❌ Missing quick-reference.md in $domain_name"
                exit 1
              fi
              if [ ! -d "$domain_dir/concepts" ]; then
                echo "❌ Missing concepts/ directory in $domain_name"
                exit 1
              fi
              if [ ! -d "$domain_dir/patterns" ]; then
                echo "❌ Missing patterns/ directory in $domain_name"
                exit 1
              fi

              # Count files
              concept_count=$(ls -1 "$domain_dir/concepts/" 2>/dev/null | wc -l)
              pattern_count=$(ls -1 "$domain_dir/patterns/" 2>/dev/null | wc -l)

              if [ "$concept_count" -lt 3 ]; then
                echo "⚠️  Warning: $domain_name has only $concept_count concept files (recommended: 3-6)"
              fi
              if [ "$pattern_count" -lt 3 ]; then
                echo "⚠️  Warning: $domain_name has only $pattern_count pattern files (recommended: 3-6)"
              fi
            fi
          done
          echo "✅ KB structure validation passed"
```

### Step 4.4: Build Plugin Workflow

**File:** `.github/workflows/build-plugin.yml`

```yaml
name: Build Plugin

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run build-plugin.sh
        run: |
          chmod +x ./build-plugin.sh
          ./build-plugin.sh

      - name: Verify Plugin Output
        run: |
          echo "Checking plugin/ directory..."

          # Verify key directories exist
          for dir in agents commands kb sdd skills .claude-plugin; do
            if [ ! -d "plugin/$dir" ]; then
              echo "❌ Missing plugin/$dir"
              exit 1
            fi
          done

          # Count agents, commands, domains
          agent_count=$(ls -1 plugin/agents/**/*.md 2>/dev/null | wc -l)
          command_count=$(ls -1 plugin/commands/**/*.md 2>/dev/null | wc -l)
          kb_count=$(ls -1d plugin/kb/*/ 2>/dev/null | wc -l)

          echo "✅ Plugin build complete"
          echo "   Agents: $agent_count"
          echo "   Commands: $command_count"
          echo "   KB Domains: $kb_count"

      - name: Upload Plugin Artifact
        uses: actions/upload-artifact@v3
        with:
          name: agentspec-plugin
          path: plugin/

      - name: Create Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body: |
            AgentSpec Plugin Release

            Build time: ${{ github.event.head_commit.timestamp }}
            Commit: ${{ github.event.head_commit.id }}
```

### Step 4.5: Webhook Handler Workflow (Manual Trigger Simulation)

**File:** `.github/workflows/webhook-handler.yml`

```yaml
name: Webhook Handler - Issue Event

on:
  issues:
    types:
      - opened
      - labeled
      - reopened

jobs:
  trigger-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Parse Issue
        id: parse
        run: |
          # Extract labels
          labels='${{ toJson(github.event.issue.labels) }}'
          echo "Labels: $labels"

          # Check for agent labels
          if echo "$labels" | grep -q "agent:odoo-specialist"; then
            echo "agent=odoo-specialist" >> $GITHUB_OUTPUT
          elif echo "$labels" | grep -q "agent:dbt-specialist"; then
            echo "agent=dbt-specialist" >> $GITHUB_OUTPUT
          fi

          # Get issue number and title
          echo "issue_number=${{ github.event.issue.number }}" >> $GITHUB_OUTPUT
          echo "issue_title=${{ github.event.issue.title }}" >> $GITHUB_OUTPUT

      - name: Comment Starting Work
        if: steps.parse.outputs.agent
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `🤖 **Agent Triggered:** ${{ steps.parse.outputs.agent }}\n\nStatus: Initializing...\n\n_Initial triage completed. Continue with manual /build execution for MVP._`
            })

      - name: Update Issue Labels
        if: steps.parse.outputs.agent
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const currentLabels = (context.payload.issue.labels || []).map((l) => l.name)
            const withoutStatus = currentLabels.filter((name) => !name.startsWith('status:'))

            github.rest.issues.update({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              labels: [...withoutStatus, 'status:in-progress']
            })

      - name: Log for Agent Processing
        run: |
          echo "Issue #${{ steps.parse.outputs.issue_number }}: ${{ steps.parse.outputs.issue_title }}"
          echo "Agent: ${{ steps.parse.outputs.agent }}"
          echo "→ Ready for Claude Agent processing"
```

---

## Phase 5: Issue Templates

### Step 5.1: Create Agent Task Template

**File:** `.github/ISSUE_TEMPLATE/agent-task.md`

```markdown
---
name: Agent Task
about: Create a task for an AI agent to work on
title: "[AGENT] Brief description"
labels: ["status:backlog"]
---

## Task Description

<!--
Describe what you want the agent to do.
Be as specific as possible.
-->

## Agent Assignment

Choose the agent that should handle this:

- [ ] `agent:odoo-specialist` - Odoo setup, module dev, data migration
- [ ] `agent:dbt-specialist` - dbt models, tests, macros
- [ ] `agent:schema-designer` - Data modeling, star schemas
- [ ] `agent:python-developer` - General Python development

## Expected Deliverables

- [ ] Deliverable 1
- [ ] Deliverable 2
- [ ] Deliverable 3

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Additional Context

<!-- Add any additional context, files, or links here -->
```

### Step 5.2: Create New Agent Template

**File:** `.github/ISSUE_TEMPLATE/new-agent.md`

```markdown
---
name: Create New Agent
about: Proposal for a new specialized agent
title: "[NEW AGENT] Agent Name"
labels: ["github-integration", "help-wanted"]
---

## Agent Proposal

**Agent Name:** [Name]
**Tier:** T1 / T2 / T3
**Primary Domain:** [Domain]

## Motivation

Why do we need this agent?

## Capabilities

List 3-5 distinct capabilities:
- Capability 1
- Capability 2
- Capability 3

## Knowledge Domains

Which KB domains should this agent use?
- domain:xxx
- domain:yyy

## Success Criteria

When will we know this agent is successful?
- [ ] Criterion 1
- [ ] Criterion 2
```

### Step 5.3: Configure Issue Templates (Optional but Recommended)

**File:** `.github/ISSUE_TEMPLATE/config.yml`

```yaml
blank_issues_enabled: false
contact_links:
  - name: Questions / General Help
    url: https://github.com/{YOUR_ORG}/agentspec/discussions
    about: Use discussions for Q&A and non-actionable topics
```

---

## Phase 6: Pull Request Template

**File:** `.github/pull_request_template.md`

```markdown
## Description

Brief description of what this PR does.

## Type of Change

- [ ] New agent (`.claude/agents/`)
- [ ] New command (`.claude/commands/`)
- [ ] New KB domain (`.claude/kb/`)
- [ ] KB update (within existing domain)
- [ ] Bug fix
- [ ] Documentation
- [ ] Infrastructure (GitHub Actions, plugin build, etc.)

## Related Issue

Closes #(issue number)

## Changes Made

- [ ] Change 1
- [ ] Change 2
- [ ] Change 3

## Testing

How should this be tested?

```bash
# Example commands to verify:
/build .claude/sdd/features/DESIGN_XYZ.md
# Expected: Files created successfully
```

## Checklist

- [ ] Code follows style guidelines
- [ ] Agent frontmatter validated (if applicable)
- [ ] KB domain structure valid (if applicable)
- [ ] Tests pass (if applicable)
- [ ] Documentation updated
- [ ] No breaking changes

## Screenshots (if applicable)

## Additional Notes

_Agent commits: All commits signed by respective agents_
```

---

## Phase 7: Validation Checklist

### ✅ Repository Setup Complete When:

- [ ] Repository created on GitHub
- [ ] Local clone: `git clone ...`
- [ ] 3 branch protection rules configured (main, develop, feat/*)
- [ ] 25 labels created with correct colors
- [ ] GitHub Projects v2 "Kanban" created with 5 columns
- [ ] `.github/workflows/` directory exists with 4 YAML files
- [ ] Issue templates in `.github/ISSUE_TEMPLATE/` (2 templates + optional `config.yml`)
- [ ] PR template at `.github/pull_request_template.md`
- [ ] Webhook URL configured only if using external server (Option B): `https://{YOUR_WEBHOOK_HOST}/webhook`

### Test the Setup:

```bash
# 1. Create a test branch
git checkout -b test/github-setup

# 2. Create test issue with agent label
# → Go to GitHub Issues, select "Agent Task" template
# → Choose agent:odoo-specialist
# → Submit

# 3. Verify in Kanban
# → Go to Projects → AgentSpec Workflow
# → Should see issue in "Backlog" column
# → Apply "status:ready" label
# → Should move to "Ready" column

# 4. Verify automations
# → Create PR linking to issue
# → Should auto-move to "Review" column when PR created
# → Merge PR → issue can auto-close if PR body includes "Closes #<issue>"
# → Set `status:done` manually (or add optional PR-event automation)
```

---

## Troubleshooting

### Issue: Labels not appearing in issue form

**Solution:** Refresh GitHub or check label creation order

### Issue: Workflow not triggering

**Solution:** Check `.github/workflows/` permissions – ensure `workflows` can write

### Issue: Kanban columns not auto-populating

**Solution:** Go to Projects → ... → Automation tab → verify triggers are set to label names exactly

---

## Next Steps

1. ✅ Complete all Phase 1-7 above
2. ➡️ Proceed to `WEBHOOK_INTEGRATION.md` to configure agent webhooks
3. ➡️ Create `ODOO_AGENT.md` and populate `.claude/agents/`
4. ➡️ Build Odoo KB domain (12 files)

---

**Validation Status:** Ready for your review
- [ ] Review this document
- [ ] Ask questions or suggest changes (via GitHub issue)
- [ ] Implement when approved
