# GitHub Agents Workflow for Small Teams (2-5 people)

> Team coordination procedures for GitHub issue lifecycle with agent automation

---

## Issue Lifecycle

```text
Created
  └─ Add labels: status:backlog, agent:*, tier:*
  └─ Agent available alert goes out
     ↓
Ready
  └─ Issue assigned with status:ready label
  └─ Agent scoped: "This will take ~2 hours"
     ↓
In Progress
  └─ Agent starts work (agent comments: "Starting...")
  └─ Creates branch: feat/name-#123
  └─ Updates label: status:in-progress
     ↓
Code Review (PR Stage)
  └─ Agent creates PR → label: status:review
  └─ Comment: "PR #456 ready for review"
     ↓
Approved
  └─ Human reviews code
  └─ Approves or requests changes
     ↓
Merged
  └─ PR merges to develop
  └─ Label set to status:done (manual or optional PR-event workflow)
  └─ Issue auto-closes when PR body contains "Closes #<issue>"
     ↓
Done
  └─ Task complete, tracked in history
```

---

## Issue State + Label Mapping

| State | Labels | Agent Action | Team Action |
|-------|--------|--------------|------------|
| **Backlog** | `status:backlog` | Monitor | Add to project |
| **Ready** | `status:ready` + `agent:*` | Accept task | Review prior PRs |
| **In Progress** | `status:in-progress` | Work + comment | Monitor Kanban |
| **Review** | `status:review` (PR exists) | Await feedback | Code review |
| **Blocked** | `status:blocked` | Escalate | Fix blocker |
| **Done** | `status:done` | Archive | Close issue |

---

## Team Size Considerations (2-5 People)

### Small Team (2 people)

```
Developer 1: Tech lead, code reviewer, DevOps
Developer 2: Feature developer, Odoo specialist

Workflow:
1. Dev1 or Dev2 creates GitHub issue
2. Agent assigned (if relevant)
3. Agent works independently
4. Whatever dev is free reviews PR
5. Quick merge, ship Daily

Git strategy: Simple, few branches
```

### Growing Team (3-5 people)

```
Lead: Project manager
Dev 1, 2, 3: Feature builders
QA / DevOps (1 person shared role)

Workflow:
1. Lead triages & labels issues
2. Assigns to agent + assigns "human owner"
3. Agent + human collaborate in comments
4. Agent creates PR; human implements fallback
5. Dev review by another dev
6. Merge to develop, then main weekly

Git strategy: Feature branches + release branch
```

---

## Case Study: "Setup Odoo 17" Issue

### Issue Creation

```markdown
Title: Setup Odoo 17 with Docker in production
Labels: agent:odoo-specialist, tier:T2, domain:odoo, status:backlog

Body:
Need production-ready Odoo 17 environment:
- Docker Compose setup
- PostgreSQL 15
- Nginx reverse proxy
- HTTPS support
- Environment variables management
- Quick start documentation

Acceptance Criteria:
- [ ] docker compose up -d works
- [ ] Odoo accessible at http://localhost
- [ ] Data persists across restart
- [ ] No hardcoded passwords
```

### Workflow Starts

**Time: 10:00 AM**

```
Issue created → GitHub Actions workflow fires
  → Posts comment: "🤖 Agent triggered: odoo-specialist"
  → Updates label: status:in-progress

Dev sees notification: "Issue #42 in progress by agent"
  → Reviews PR status in GitHub Projects Kanban
  → Issue moved to "In Progress" column
```

**Time: 10:05 AM** — Agent Works

Agent (Claude in headless mode via GitHub):
1. Analyzes issue requirements
2. Loads Odoo KB (concepts + patterns)
3. Generates docker-compose.yml, .env.example, configs
4. Comments on issue: "Starting work. ETA: 1-2 hours"
5. Creates branch: `feat/odoo-setup-#42`
6. Commits 7 files

**Time: 11:30 AM** — PR Created

Agent:
1. Creates PR #123: "Setup Odoo 17 Docker #42"
2. Generates PR body from DESIGN document
3. Comments on issue: "PR #123 ready for review"
4. Updates label: status:review

Team sees:
- Kanban moves issue to "Review" column
- PR appears in GitHub inbox
- 7 files generated ready for review

**Time: 11:45 AM** — Code Review

Developer reviews:
```
✓ docker-compose.yml structure
✓ .env templating approach
✓ Nginx config with security headers
✓ Odoo config parameters
? Should we add backup script?
```

Comment on PR:
```markdown
Great work! A few notes:
- [ ] Can you add a backup.sh script?
- [ ] Document the 10-minute quickstart
- [ ] Add to README

Otherwise ready to merge.
```

**Time: 12:00 PM** — Agent Responds

If agent has "improve-based-on-feedback" capability:
```markdown
✓ Added: scripts/backup.sh
✓ Added: QUICKSTART.md
✓ Updated: README.md with setup section

Ready to merge! 🚀
```

**Time: 12:15 PM** — Merge to Production

Developer:
1. Approves PR #123
2. Merges to `develop` branch
3. GitHub automatically:
   - Closes issue #42 (if PR body includes closing keyword)
   - Moves Kanban item to "Done" (Project automation)
   - Tags in release notes
4. Team updates label to `status:done` (or uses optional PR-event automation)

Issue complete in ~2 hours, end-to-end.

---

## Comment Templates for Team

### When Assigning Task to Agent

```markdown
🎯 **Assigned to:** @agent:odoo-specialist

Agent priority: P1 (high)
Expected time: 1-2 hours
Complexity: Medium

Agent, please:
1. Confirm you have all info needed
2. Create PR when ready
3. Update status labels as you progress

Team, please don't start any related work...
```

### When Requesting Changes from Agent

```markdown
@agent-pr Thanks for the work!

Requests:
- [ ] Add error handling for DB connection failures
- [ ] Document the admin password setup
- [ ] Add unit tests for the custom module

Otherwise looks good. Can you iterate?
```

### When Agent is Blocked

```markdown
⚠️ **Agent Escalation**

@lead — This task requires:
- [ ] Security review of DB credentials approach
- [ ] Decision on SSL certificate strategy

Status: `status:blocked` — waiting for guidance.

Agent on standby, ready to resume when approved.
```

### When Merging Agent's Work

```markdown
✅ **Merged to Develop**

@agent-odoo-specialist — Great work! Merged PR #123 to develop.

Deployment planned for: Friday 5pm
Release notes updated: [CHANGELOG](./CHANGELOG.md)

Status: `status:done`
Issue: Closed

Thanks for the help! 🚀
```

---

## Multi-Agent Coordination

### When 2 Agents Work Together

**Issue:** "Build Odoo module + import data + optimize queries"

```markdown
**Assigned Agents:**
- @odoo-specialist (module development)
- @data-engineer (import scripts)
- @sql-optimizer (query tuning)

Workflow:
1. odoo-specialist: Creates module structure
2. data-engineer: Builds import script
3. sql-optimizer: Tunes the queries
4. All commit to same PR #456
5. Human does single review
6. Merge once
```

### Agent Handoff Pattern

```
odoo-specialist finishes module
  └─ Comment: "@schema-designer — Need DB optimization advice"

schema-designer reviews + comments
  └─ "Suggest ADD INDEX on (partner_id, date)"

odoo-specialist applies suggestion
  └─ Updates code, recommits

Final PR includes both contributions
```

---

## Weekly Review Cadence

### Monday 9 AM: Sprint Planning

- [ ] Review backlog issues
- [ ] Assign `status:ready` to doable issues
- [ ] Tag with agent labels
- [ ] Estimate effort

### Wednesday 3 PM: Midweek Check-in

- [ ] Review "In Progress" items
- [ ] Identify blockers
- [ ] Approve any pending PRs

### Friday 4 PM: Sprint Close

- [ ] All "Review" PRs approved or commented
- [ ] Merge ready items
- [ ] Move "Done" items to release notes
- [ ] Plan next week

---

## Troubleshooting

### Issue: Agent Creates PR but No Comment

**Solution:**
```
Wait 2 minutes (webhook delay)
Manually check agent status in Discord/Slack
If stuck: Click "run workflow" in Actions tab
```

### Issue: Multiple Agents Touch Same Files

**Solution:**
```
Create separate feature branches:
- feat/odoo-setup-#42
- feat/odoo-import-#43

Merge in order to prevent conflicts
```

### Issue: Agent Escalates but No Response

**Solution:**
```
Dev assigned to @team should monitor escalations
Check "Blocked" column in Kanban
Respond to agent within 4 hours
```

---

## Validation Checklist

### ✅ Team Workflow Ready When:

- [ ] All team members understand issue lifecycle
- [ ] Labels in use consistently
- [ ] Kanban automatically synced
- [ ] Code review process documented
- [ ] Comment templates copied to wiki
- [ ] Escalation paths clear
- [ ] Weekly cadence scheduled

---

**Status:** Ready for team training
- [ ] Share this doc with team
- [ ] Walk through case study together
- [ ] Do a test run with dummy issue #1
- [ ] Iterate feedback
