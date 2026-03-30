# GitHub Webhook Integration for Agent Automation

> Automated workflow: GitHub Issue created → Webhook fires → Claude Agent processes → Comments + PR created

**Target:** Webhook integration for small team (2-5 people) where creating a GitHub issue automatically triggers an AI agent to work on it.

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────┐
│                    WEBHOOK AUTOMATION FLOW                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  1. User creates GitHub Issue (#123)                                 │
│     └─ Title: "Setup Odoo 17 with Docker"                            │
│     └─ Label: agent:odoo-specialist, status:ready                    │
│                                                                        │
│  2. GitHub fires webhook event                                        │
│     └─ POST /webhook (your server or GitHub Actions)                │
│     └─ Payload: issue details + labels                              │
│                                                                        │
│  3. Webhook handler analyzes issue                                    │
│     └─ Extract agent label → odoo-specialist                        │
│     └─ Extract task description                                      │
│     └─ Check for blocking issues                                     │
│                                                                        │
│  4. Agent is invoked via Claude API                                   │
│     └─ Agent loads Odoo KB                                           │
│     └─ Analyzes task → generates solution                            │
│                                                                        │
│  5. Agent posts progress comments                                     │
│     └─ Comment: "Starting task. ETA: 2 hours"                       │
│     └─ Create PR: feat/odoo-setup-#123                              │
│     └─ Update label: status:in-progress                              │
│                                                                        │
│  6. Agent completes work                                              │
│     └─ Final comment: "Complete! PR ready for review"               │
│     └─ Update label: status:review                                   │
│                                                                        │
│  7. Human reviews + merges                                            │
│     └─ Review PR in `feat/odoo-setup-#123`                          │
│     └─ Merge to develop                                              │
│     └─ Set status:done manually (or via optional PR workflow)        │
│     └─ Close issue (automatic if PR body contains "Closes #...")     │
│                                                                        │
│  Kanban synced automatically ↔ Labels ↔ Project columns             │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Webhook Setup (GitHub → Your Server)

### Option A: GitHub Actions Workflow (Recommended for MVP)

**Trigger:** Issue created or labeled

**File:** Already created in `.github/workflows/webhook-handler.yml` (see GITHUB_SETUP.md Phase 4.5)

**What it does:**
- Listens for `issue.opened` and `issue.labeled` events
- Extracts agent label (`agent:odoo-specialist`)
- Posts initial comment
- Updates status label to `status:in-progress` (preserving non-status labels)
- Logs event for manual agent processing

**Limitation:** This is a **synchronous trigger**. For actual agent execution, you'll need to:
1. Manually invoke `/build` or `/design` command in Claude Code
2. Reference the GitHub issue number
3. Agent comments back to issue

### Option B: Webhook Server (Advanced)

For true automation without manual triggering, set up a webhook server:

```python
# Example: Python Flask server (not included in MVP)
from flask import Flask, request
import requests
import json

app = Flask(__name__)
CLAUDE_API_KEY = os.environ['CLAUDE_API_KEY']

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    payload = request.json

    if payload['action'] == 'opened' or payload['action'] == 'labeled':
        issue = payload['issue']
        labels = [label['name'] for label in issue['labels']]

        # Find agent label
        agent = None
        for label in labels:
            if label.startswith('agent:'):
                agent = label.split(':')[1]
                break

        if agent:
            # Call Claude API to invoke agent
            invoke_agent(agent, issue)

    return {'status': 'ok'}, 200

def invoke_agent(agent: str, issue: dict):
    # Call Claude API with agent + issue details
    prompt = f"""
    GitHub Issue #{issue['number']}: {issue['title']}

    Description: {issue['body']}

    Please process this task and comment on the GitHub issue when complete.
    """

    # Call Claude API (requires Agent SDK)
    # ... implementation details ...
```

**For MVP:** Use GitHub Actions workflow (Option A) + manual `/build` invocation

---

## Phase 2: Agent Invocation (Manual MVP)

### Step 1: Create Issue in GitHub

```markdown
Title: Setup Odoo 17 with Docker
Labels: agent:odoo-specialist, status:ready

Body:
- Odoo version: 17
- Database: PostgreSQL 15
- Environment: development
- Docker Compose needed
- Document the setup process
```

### Step 2: Workflow Automation Happens

**GitHub Actions workflow runs:**
```
✓ Detect issue.opened event
✓ Extract labels: agent:odoo-specialist
✓ Post comment: "🤖 Agent triggered"
✓ Update status label: status:in-progress
✓ Workflow completes
```

### Step 3: Human Triggers Agent in Claude Code

In Claude Code IDE:

```
/build

## Input
Issue: #123 - Setup Odoo 17 with Docker
Agent: odoo-specialist
```

### Step 4: Agent Works + Comments

Agent automatically:

1. **Reads GitHub Issue** (issue #123 content)
2. **Loads Odoo KB** (concepts + patterns)
3. **Generates Solution** (Docker Compose + code)
4. **Posts Progress Comment**
   ```markdown
   🤖 **odoo-specialist** — Task #123

   ✓ Analyzed requirements
   ✓ Generated Docker Compose setup
   ✓ Created Odoo config

   Next: Create PR with files
   ETA: 2 hours total
   ```
5. **Creates PR Automatically**
   - Branch: `feat/odoo-setup-#123`
   - Files: docker-compose.yml, .env.example, odoo/config/, nginx/conf.d/
6. **Updates GitHub Issue**
   - Label: `status:review` (instead of `status:in-progress`)
   - Comment: "PR #456 ready for review"

---

## Phase 3: Comment Templates

### Template 1: Task Started

```markdown
🤖 **{agent-name}** — Task Started

**Issue:** #{issue_number}: {issue_title}

**Analysis:**
- Requirements understood ✓
- KB domains loaded: odoo, python, data-modeling
- Confidence: 0.95 (IMPORTANT)

**Approach:**
1. Generate Docker Compose scaffold
2. Create Odoo config files
3. Generate documentation

**Estimated Time:** ~1-2 hours

---
_Agent: {agent-name} | Confidence: 0.95_
```

### Template 2: Checkpoint / Progress Update

```markdown
✅ **{agent-name}** — Progress Update

**Issue:** #{issue_number}

**Completed:**
- [x] Docker Compose generated
- [x] PostgreSQL config set
- [x] Nginx reverse proxy configured

**In Progress:**
- [ ] Odoo config files

**Next:**
- [ ] Testing configuration
- [ ] Generate PR with all files

**ETA Remaining:** ~30 minutes

---
_Agent: {agent-name} | Confidence: 0.95_
```

### Template 3: Task Complete + PR Created

```markdown
✅ **{agent-name}** — Task Complete

**Issue:** #{issue_number}: {issue_title}

**Deliverables:**
- ✅ `docker-compose.yml` — Odoo + PostgreSQL + Nginx orchestration
- ✅ `.env.example` — Environment variables template
- ✅ `odoo/config/odoo.conf` — Odoo configuration
- ✅ `nginx/conf.d/odoo.conf` — Reverse proxy setup

**PR Created:** #456 (`feat/odoo-setup-#123`)

**Quick Start:**
```bash
cp .env.example .env
docker compose up -d
```

**Next Steps:**
1. Review PR #456
2. Test locally: `docker compose ps`
3. Merge to develop
4. Deploy to production

---
_Agent: {agent-name} | Confidence: 0.95_
_All tests passing ✓_
```

### Template 4: Escalation Required

```markdown
⚠️ **{agent-name}** — Escalation Required

**Issue:** #{issue_number}

**Reason:** {Explain why agent can't proceed}

**Required Action:**
- 🚀 Escalated to: @python-developer
- 📋 Reason: Code review needed for security compliance
- 📌 Issue: #123 (link)

**Next Steps:**
1. @python-developer reviews code
2. Provide feedback in comments
3. Agent updates code
4. Return to review status

**Status:** `status:blocked` (temporarily)

---
_Agent: {agent-name} | Confidence: 0.70 (below threshold)_
```

### Template 5: Issue Found + Halted

```markdown
❌ **{agent-name}** — Task Halted

**Issue:** #{issue_number}

**Problem:** {Describe why task can't proceed}

**Error Details:**
```
[Error message or stack trace]
```

**Required Human Action:**
1. [ ] Fix: {specific action needed}
2. [ ] Verify: {what to check}
3. [ ] Reopen issue with label `status:ready`

**Agent will retry** when issue is re-labeled.

---
_Agent: {agent-name} | Status: HALTED_
```

---

## Phase 4: Agent → GitHub Integration

### Action 1: Post Comment on Issue

```python
# Pseudo-code (agent SDK)
agent.comment_on_issue(
    issue_number=123,
    body="""
    ✅ Task complete!

    Generated files:
    - docker-compose.yml
    - .env.example
    - odoo/config/odoo.conf
    """
)
```

### Action 2: Create/Update Branch

```bash
# Agent creates branch
git checkout -b feat/odoo-setup-#123

# Make changes
# ... (write files)

# Commit
git add .
git commit -m "feat: Odoo 17 Docker setup for #123

- Docker Compose with Odoo, PostgreSQL, Nginx
- Environment variables template
- Production-ready configuration

Closes #123"

# Push
git push origin feat/odoo-setup-#123
```

### Action 3: Create Pull Request

```python
# Agent creates PR
agent.create_pull_request(
    title="feat: Odoo 17 Docker setup #123",
    description="""
    ## Summary
    Complete Docker Compose setup for Odoo 17 production environment.

    ## Changes
    - docker-compose.yml with 3 services (odoo, postgres, nginx)
    - Configuration templates for environment variables
    - Nginx reverse proxy with gzip + security headers

    ## Testing
    ```bash
    cp .env.example .env
    docker compose up -d
    docker compose ps  # verify all running
    ```

    ## Closes
    #123
    """,
    base="develop",
    head="feat/odoo-setup-#123"
)
```

### Action 4: Update Issue Labels

```python
# Agent updates labels
agent.update_issue_labels(
    issue_number=123,
    remove_labels=["status:in-progress"],
    add_labels=["status:review"]
)
```

### Action 5: Add Reactions

```python
# Agent reacts to comments (optional)
agent.add_reaction(
    issue_number=123,
    comment_id=12345,
    reaction="+1"  # or 'rocket', 'eyes', etc.
)
```

---

## Phase 5: Error Handling & Fallbacks

### Error 1: Issue Not Properly Labeled

**Detection:**
```python
if 'agent:' not in labels:
    # No agent assignment
    post_comment("Please assign an agent label (e.g., agent:odoo-specialist)")
    return
```

**Recovery:**
- Comment asking for label
- Do NOT start work
- Wait for label

### Error 2: Conflicting Issue Labels

**Detection:**
```python
agents = [l for l in labels if l.startswith('agent:')]
if len(agents) > 1:
    # Multiple agents assigned
    post_comment(f"Multiple agents assigned: {agents}. Please pick ONE.")
    return
```

### Error 3: Data Loss Risk in Migration

**Detection:**
```python
if "migrate" in title.lower() and "backup" not in description.lower():
    post_comment("⚠️ Data migration without backup plan. Require confirmation.")
    agent.escalate_to_user()
    return
```

### Error 4: PR Creation Failed

**Fallback:**
```python
try:
    create_pr(...)
except GitHubAPIError:
    post_comment("PR creation failed. Manual steps to review code: [...]")
    update_label("status:blocked")
```

---

## Phase 6: Testing Webhook Locally

### Test 1: Manual Webhook Simulation

```bash
# Simulate GitHub webhook event
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "action": "opened",
    "issue": {
      "number": 123,
      "title": "Test Odoo Setup",
      "body": "Setup Odoo with Docker",
      "labels": [
        {"name": "agent:odoo-specialist"},
        {"name": "status:ready"}
      ]
    }
  }'
```

### Test 2: GitHub Actions Dry-Run

```bash
# Check workflow syntax
gh workflow list
gh workflow view webhook-handler.yml --json

# View recent runs
gh run list --workflow=webhook-handler.yml
```

### Test 3: Create Real Issue & Watch

1. Create issue with label `agent:odoo-specialist`
2. Watch GitHub Actions run in "Actions" tab
3. Verify workflow completes successfully
4. Check issue comments for agent initiation

---

## Phase 7: Validation Checklist

### ✅ Webhook Integration Ready When:

- [ ] `.github/workflows/webhook-handler.yml` exists
- [ ] 5 comment templates created (started, checkpoint, complete, escalation, error)
- [ ] GitHub Actions workflow tested (creates dummy comment)
- [ ] Agent labels in use (agent:odoo-specialist, agent:dbt-specialist, etc.)
- [ ] Issue events update to `status:in-progress` automatically without removing non-status labels
- [ ] `status:review` and `status:done` are handled manually or by optional PR-event automation
- [ ] Sample issue created & workflow tested
- [ ] PR creation template created (`.github/pull_request_template.md`)
- [ ] Escalation routes documented (when agent hands off)
- [ ] Error handling procedures documented

### Manual Test Procedure

```bash
# Step 1: Create test issue
gh issue create \
  --title "Test Webhook - Setup Odoo" \
  --body "Test trigger for odoo-specialist agent" \
  --label "agent:odoo-specialist" \
  --label "status:ready"

# Step 2: Watch Actions tab
# Go to GitHub repo → Actions → workflow-handler.yml

# Step 3: Verify comment posted
# Refresh issue → Should see bot comment "🤖 Agent Triggered"

# Step 4: Check label update
# Issue should have label "status:in-progress"

# Step 5: Manual agent invocation (in Claude Code)
# /build issue-123
```

---

## Next Steps

1. ✅ GitHub workflow created (GITHUB_SETUP.md)
2. ✅ Comment templates defined (this document)
3. ➡️ Test with real issue #1
4. ➡️ Integrate with `ODOO_AGENT.md` capabilities
5. ➡️ Create `GITHUB_AGENTS_WORKFLOW.md` for team procedures

---

**Status:** Ready for your validation
- [ ] Review webhook flow
- [ ] Test locally with sample issue
- [ ] Approve comment templates
- [ ] Proceed to implement
