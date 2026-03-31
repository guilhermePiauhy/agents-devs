"""
GitHub-native workflow — triggered by issue labels.

SDD Feature phases:
  sdd:brainstorm  → Explore the idea, generate BRAINSTORM doc
  sdd:define      → Extract requirements, generate DEFINE doc
  sdd:design      → Technical architecture, generate DESIGN doc
  sdd:build       → Generate code + open PR in target repo
  sdd:ship        → Archive, lessons learned, close issue

Bugfix phases:
  bug:diagnose    → Analyze bug, identify root cause, propose fix
  bug:fix         → Generate patch + open PR in target repo
  bug:close       → Verification checklist + close issue

Target repo is parsed from the issue body:
  **Target Repo:** owner/repo
"""

import json
import os
import re
import sys
import time

import anthropic
import requests

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GH_PAT = os.environ.get("GH_PAT", GITHUB_TOKEN)
ISSUE_NUMBER = os.environ["ISSUE_NUMBER"]
ISSUE_TITLE = os.environ["ISSUE_TITLE"]
ISSUE_BODY = os.environ["ISSUE_BODY"]
LABEL_NAME = os.environ["LABEL_NAME"]  # e.g. "sdd:brainstorm"
REPO = os.environ["REPO"]              # e.g. "guilhermePiauhy/agents-devs"

PHASE = LABEL_NAME.replace("sdd:", "")  # e.g. "brainstorm"

# ---------------------------------------------------------------------------
# GitHub helpers
# ---------------------------------------------------------------------------
GH_HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

GH_PAT_HEADERS = {
    "Authorization": f"Bearer {GH_PAT}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def gh_get(url, headers=None):
    resp = requests.get(url, headers=headers or GH_HEADERS)
    resp.raise_for_status()
    return resp.json()


def gh_post(url, payload, headers=None):
    resp = requests.post(url, headers=headers or GH_HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()


def gh_put(url, payload, headers=None):
    resp = requests.put(url, headers=headers or GH_HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()


def get_issue_comments():
    url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}/comments?per_page=100"
    return gh_get(url)


def post_comment(body: str):
    url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}/comments"
    gh_post(url, {"body": body})
    print("Comment posted.")


def close_issue():
    url = f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}"
    requests.patch(url, headers=GH_HEADERS, json={"state": "closed"}).raise_for_status()
    print("Issue closed.")


# ---------------------------------------------------------------------------
# Context builder
# ---------------------------------------------------------------------------
def extract_target_repo(text: str) -> str | None:
    match = re.search(
        r"[Tt]arget\s*[Rr]epo[:\s*`]+([a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+)",
        text,
    )
    return match.group(1).strip() if match else None


def build_context(max_chars: int = 12000) -> tuple[str, str | None]:
    """Returns (full_context_markdown, target_repo_or_None)

    Limits context to max_chars to prevent token overflow on large issues.
    Keeps most recent comments first, then truncates if needed.
    """
    comments = get_issue_comments()

    context = f"# Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}\n\n{ISSUE_BODY}\n\n"

    target_repo = extract_target_repo(ISSUE_BODY)

    if comments:
        context += "---\n\n## Discussion & Previous Documents\n\n"
        # Reverse to show most recent first
        for c in reversed(comments[-5:]):  # Only last 5 comments to save space
            author = c["user"]["login"]
            body = c["body"]
            # Truncate very long comments
            body_preview = body[:1000] if len(body) > 1000 else body
            context += f"### Comment by @{author}\n\n{body_preview}\n\n---\n\n"
            if not target_repo:
                target_repo = extract_target_repo(body)

    # Truncate context if too large
    if len(context) > max_chars:
        context = context[:max_chars] + "\n\n[... contexto truncado ...]"

    return context, target_repo


# ---------------------------------------------------------------------------
# Phase prompts
# ---------------------------------------------------------------------------
PHASE_ICON = {
    "brainstorm": "🧠",
    "define": "📋",
    "design": "🏗️",
    "build": "🔨",
    "ship": "🚀",
    "diagnose": "🔍",
    "fix": "🩹",
    "close": "✅",
}

PROMPTS = {
    "brainstorm": """\
You are an AgentSpec SDD brainstorm facilitator working inside a GitHub issue.

Generate a **BRAINSTORM document** based on the issue context below.

Structure your response as:
## 🧠 BRAINSTORM: {title}

### Problem Statement
(what problem are we solving?)

### Ideas & Approaches
(2-4 possible approaches with brief trade-offs)

### Key Questions
(unknowns that must be answered before defining requirements)

### Success Criteria
(how will we know this is done?)

### Risks
(technical, scope, or timeline risks)

### Recommended Next Step
(what the /define phase should focus on)

---
Issue context:
{context}
""",

    "define": """\
You are an AgentSpec SDD requirements specialist working inside a GitHub issue.

Based on the brainstorm and discussion below, generate a **DEFINE document**.

Structure your response as:
## 📋 DEFINE: {title}

### Functional Requirements
| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | ... | Must |

### Non-Functional Requirements
| ID | Requirement |
|----|-------------|
| NFR-001 | ... |

### Out of Scope
(explicit list of what will NOT be built)

### Acceptance Criteria
(testable conditions for "done")

### Dependencies
(other systems, repos, or work this depends on)

### Open Questions
(questions that must be resolved before design)

---
Context:
{context}
""",

    "design": """\
You are an AgentSpec SDD architect working inside a GitHub issue.

Based on the requirements below, generate a **DESIGN document**.

Structure your response as:
## 🏗️ DESIGN: {title}

### Architecture Overview
(2-3 sentences describing the approach)

### Component Diagram
```
(ASCII diagram of components and their relationships)
```

### Files to Create / Modify
| File | Action | Purpose |
|------|--------|---------|
| path/to/file | CREATE | ... |

### Implementation Plan
(ordered steps, each tied to requirements)

### Technical Decisions
(key choices made and why)

### Risks & Mitigations
| Risk | Mitigation |
|------|------------|

---
Context:
{context}
""",

    "build": """\
Generate a BUILD PLAN as JSON ONLY from the DESIGN specification.

{{
  "branch": "feat/feature-name",
  "pr_title": "feat: description",
  "pr_body": "## Summary\\n- Implements FR-001, FR-002\\n- Resolves issue #{issue_number}",
  "files": [
    {{"path": "docker-compose.yml", "lang": "yaml"}},
    {{"path": "config/app.conf", "lang": "ini"}}
  ]
}}

DESIGN SPECIFICATION:
{context}

Rules:
- Only respond with valid JSON object, nothing else
- List files from "Files to Create" section of DESIGN
- Extract branch from DESIGN or suggest logical name
""",

    "build_content": """\
Generate the complete, production-ready file content based on the DESIGN.

File: {file_path}
Language: {language}

DESIGN SPECIFICATION (for reference):
{context}

Output ONLY the file content - no markdown fences, no explanations.
""",

    "ship": """\
You are an AgentSpec SDD ship specialist working inside a GitHub issue.

Based on the full context below, generate a **SHIP document** that closes this feature.

Structure your response as:
## 🚀 SHIPPED: {title}

### What Was Built
(summary of deliverables)

### Where It Lives
(repo, branch, PR links if known)

### Lessons Learned
(what worked well, what to improve next time)

### Follow-up Tasks
(known limitations or future improvements — create new issues for these)

### Status
✅ Feature shipped and issue closed.

---
Context:
{context}
""",

    # ------------------------------------------------------------------
    # Bugfix phases
    # ------------------------------------------------------------------

    "diagnose": """\
You are an expert software debugger working inside a GitHub issue.

Based on the bug report below, generate a **DIAGNOSE document**.

Structure your response as:
## 🔍 DIAGNOSE: {title}

### Bug Summary
(one paragraph describing what is broken and the observed vs expected behavior)

### Likely Root Cause
(your best analysis of what is causing this — be specific about files, functions, or config if mentioned)

### Reproduction Steps
(minimal steps to reproduce, inferred from the report)

### Affected Areas
| Area | File / Component | Confidence |
|------|-----------------|------------|
| ... | ... | High/Medium/Low |

### Proposed Fix Approach
(concrete description of what needs to change to fix the bug)

### Risk Assessment
(could this fix break anything else?)

### Next Step
Add label `bug:fix` to generate the patch and open a PR.

---
Bug report:
{context}
""",

    "fix": """\
You are an expert software engineer fixing a bug inside a GitHub issue.

Based on the diagnosis and full context below, generate ALL files needed to fix this bug.

IMPORTANT: Respond with ONLY a valid JSON object — no markdown, no explanation, just the JSON:

{{
  "branch": "fix/short-bug-description",
  "pr_title": "fix: short description of the fix",
  "pr_body": "## Fix Summary\\n\\n- What was broken\\n- What was changed\\n- How to verify\\n\\nFixes #{issue_number}",
  "fix_summary": "2-3 sentence summary of the fix",
  "files": [
    {{
      "path": "relative/path/to/file.ext",
      "content": "full corrected file content"
    }}
  ]
}}

Rules:
- "branch" must start with fix/
- Include ONLY files that need to change to fix the bug
- Every file must contain the complete corrected content — not just the diff
- "pr_body" must reference: Fixes #{issue_number}

Context:
{context}
""",

    "close": """\
You are a QA engineer closing a bug issue on GitHub.

Based on the full context below (bug report, diagnosis, fix PR), generate a **CLOSE document**.

Structure your response as:
## ✅ BUG CLOSED: {title}

### Fix Summary
(what was changed and why it resolves the bug)

### Verification Checklist
- [ ] PR merged in target repo
- [ ] (specific test step 1 derived from the bug report)
- [ ] (specific test step 2)
- [ ] No regressions in related areas

### Root Cause (confirmed)
(final confirmed root cause)

### Prevention
(what could prevent this class of bug in the future — tests, linting, etc.)

### Status
✅ Bug fixed, verified, and issue closed.

---
Context:
{context}
""",
}


# ---------------------------------------------------------------------------
# Claude API
# ---------------------------------------------------------------------------
def call_claude(prompt: str, max_tokens: int = 4096) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Build phase — create files in target repo and open PR
# ---------------------------------------------------------------------------
def get_default_branch(target_repo: str) -> str:
    data = gh_get(f"https://api.github.com/repos/{target_repo}", headers=GH_PAT_HEADERS)
    return data["default_branch"]


def get_branch_sha(target_repo: str, branch: str) -> str:
    data = gh_get(
        f"https://api.github.com/repos/{target_repo}/git/ref/heads/{branch}",
        headers=GH_PAT_HEADERS,
    )
    return data["object"]["sha"]


def create_branch(target_repo: str, branch: str, from_sha: str):
    gh_post(
        f"https://api.github.com/repos/{target_repo}/git/refs",
        {"ref": f"refs/heads/{branch}", "sha": from_sha},
        headers=GH_PAT_HEADERS,
    )
    print(f"Branch created: {branch}")


def create_file(target_repo: str, path: str, content: str, branch: str, message: str):
    import base64
    encoded = base64.b64encode(content.encode()).decode()
    # Check if file exists to get its SHA (needed for updates)
    sha = None
    try:
        existing = gh_get(
            f"https://api.github.com/repos/{target_repo}/contents/{path}?ref={branch}",
            headers=GH_PAT_HEADERS,
        )
        sha = existing.get("sha")
    except requests.HTTPError:
        pass

    payload = {"message": message, "content": encoded, "branch": branch}
    if sha:
        payload["sha"] = sha

    gh_put(
        f"https://api.github.com/repos/{target_repo}/contents/{path}",
        payload,
        headers=GH_PAT_HEADERS,
    )


def create_pr(target_repo: str, branch: str, base: str, title: str, body: str) -> str:
    data = gh_post(
        f"https://api.github.com/repos/{target_repo}/pulls",
        {"title": title, "body": body, "head": branch, "base": base},
        headers=GH_PAT_HEADERS,
    )
    return data["html_url"]


def execute_build(context: str, target_repo: str) -> str:
    """Two-phase build: Phase 1 = plan, Phase 2 = generate content for each file"""

    # PHASE 1: Generate build plan (file list only, no content)
    print("Phase 1: Generating build plan from DESIGN...")
    plan_prompt = PROMPTS["build"].format(
        context=context,  # Full DESIGN document
        issue_number=ISSUE_NUMBER,
    )
    raw_plan = call_claude(plan_prompt, max_tokens=1500)  # Enough for file list
    raw_plan = re.sub(r"^```(?:json)?\s*", "", raw_plan.strip())
    raw_plan = re.sub(r"\s*```$", "", raw_plan.strip())

    try:
        plan = json.loads(raw_plan)
    except json.JSONDecodeError as e:
        raise ValueError(f"Build plan JSON invalid: {e}\n\nRaw:\n{raw_plan[:300]}")

    branch = plan["branch"]
    pr_title = plan["pr_title"]
    pr_body = plan["pr_body"]
    file_specs = plan["files"]  # {path, lang}
    build_summary = plan.get("build_summary", "")

    print(f"Target repo: {target_repo}")
    print(f"Branch: {branch}")
    print(f"Files planned: {len(file_specs)}")

    default_branch = get_default_branch(target_repo)
    base_sha = get_branch_sha(target_repo, default_branch)
    create_branch(target_repo, branch, base_sha)

    # PHASE 2: Generate content for each file (separate API calls)
    created_files = []
    for i, spec in enumerate(file_specs):
        file_path = spec["path"]
        language = spec.get("lang", "text")

        print(f"  [{i+1}/{len(file_specs)}] Generating content for {file_path}...")

        content_prompt = PROMPTS["build_content"].format(
            file_path=file_path,
            language=language,
            context=context,  # Full DESIGN for each file
        )

        try:
            content = call_claude(content_prompt, max_tokens=2048)  # Enough for file content
            content = content.strip()

            create_file(
                target_repo,
                file_path,
                content,
                branch,
                f"feat: add {file_path}",
            )
            created_files.append(file_path)
            print(f"    ✅ {file_path}")
            time.sleep(0.3)  # avoid rate limiting

        except Exception as e:
            print(f"    ⚠️ Failed to generate {file_path}: {e}")
            # Continue with other files instead of failing entirely

    pr_url = create_pr(target_repo, branch, default_branch, pr_title, pr_body)
    print(f"PR created: {pr_url}")

    file_list = "\n".join(f"- `{f}`" for f in created_files)
    return (
        f"## 🔨 BUILD EXECUTED: {ISSUE_TITLE}\n\n"
        f"{build_summary}\n\n"
        f"### Files created ({len(created_files)}/{len(file_specs)})\n{file_list}\n\n"
        f"### Pull Request\n"
        f"➡️ **[{pr_title}]({pr_url})**\n\n"
        f"Review and merge the PR in `{target_repo}` to complete this phase."
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def get_design_file_path() -> str:
    """Returns path to design document for this issue."""
    # Sanitize title to filename (replace spaces/special chars)
    safe_title = re.sub(r'[^a-zA-Z0-9_-]', '_', ISSUE_TITLE)[:50]
    return f".claude/sdd/features/DESIGN_{safe_title}_#{ISSUE_NUMBER}.md"


def save_design_doc(result: str):
    """Save design document to repo for later use by build phase."""
    try:
        design_path = get_design_file_path()
        # This would need to be committed to the repo
        # For now, we just mark it in the comment for manual save
        print(f"Design should be saved to: {design_path}")
    except Exception as e:
        print(f"Warning: Could not save design: {e}")


def load_design_context() -> str:
    """Try to load DESIGN doc from repo if it exists."""
    design_path = get_design_file_path()
    try:
        # Try to read from workspace
        with open(design_path, 'r') as f:
            content = f.read()
            print(f"Loaded design from {design_path}")
            return content
    except FileNotFoundError:
        print(f"Design file not found at {design_path}")
        return ""


def main():
    print(f"Phase: {PHASE} | Label: {LABEL_NAME} | Issue: #{ISSUE_NUMBER} | Repo: {REPO}")

    if PHASE not in PROMPTS:
        print(f"Unknown phase: {PHASE}. Valid: {list(PROMPTS.keys())}")
        sys.exit(1)

    context, target_repo = build_context()
    print(f"Target repo: {target_repo or 'not specified'}")

    footer = (
        f"\n\n---\n"
        f"*AgentSpec — Phase **{PHASE_ICON.get(PHASE, '')} {PHASE.title()}** "
        f"| Label `{LABEL_NAME}` on issue #{ISSUE_NUMBER}*"
    )
    if target_repo:
        footer += f"\n*Target: [{target_repo}](https://github.com/{target_repo})*"

    # Phases that generate code and open a PR
    if PHASE in ("build", "fix"):
        if not target_repo:
            post_comment(
                f"❌ **{PHASE.title()} failed:** No `Target Repo` found in this issue.\n\n"
                "Add a line like:\n```\n**Target Repo:** owner/repo\n```\n"
                f"Then re-add the `{LABEL_NAME}` label."
            )
            sys.exit(1)

        # For build phase, try to load design doc for rich context
        if PHASE == "build":
            design_context = load_design_context()
            if design_context:
                context = design_context  # Use design as primary context
            # Fallback to issue context if no design found

        result = execute_build(context, target_repo)
        post_comment(result + footer)

    else:
        prompt = PROMPTS[PHASE].format(
            title=ISSUE_TITLE,
            context=context,
            issue_number=ISSUE_NUMBER,
        )
        print("Calling Claude API...")
        result = call_claude(prompt)
        post_comment(result + footer)

        # After design phase, suggest saving to file
        if PHASE == "design":
            save_design_doc(result)
            post_comment(
                f"\n\n💾 **Next step:** Save this DESIGN doc to:\n"
                f"```\n{get_design_file_path()}\n```\n"
                f"Then add the label `sdd:build` to use it for code generation."
            )

        # Close issue on final phases
        if PHASE in ("ship", "close"):
            close_issue()

    print("Done.")


if __name__ == "__main__":
    main()
