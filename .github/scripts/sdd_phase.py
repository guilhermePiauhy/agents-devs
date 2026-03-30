"""
SDD GitHub-native workflow — triggered by issue labels.

Label → Phase:
  sdd:brainstorm  → Explore the idea, generate BRAINSTORM doc
  sdd:define      → Extract requirements, generate DEFINE doc
  sdd:design      → Technical architecture, generate DESIGN doc
  sdd:build       → Generate code + open PR in target repo
  sdd:ship        → Archive, lessons learned, close issue

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


def build_context() -> tuple[str, str | None]:
    """Returns (full_context_markdown, target_repo_or_None)"""
    comments = get_issue_comments()

    context = f"# Issue #{ISSUE_NUMBER}: {ISSUE_TITLE}\n\n{ISSUE_BODY}\n\n"

    target_repo = extract_target_repo(ISSUE_BODY)

    if comments:
        context += "---\n\n## Discussion & Previous Documents\n\n"
        for c in comments:
            author = c["user"]["login"]
            body = c["body"]
            context += f"### Comment by @{author}\n\n{body}\n\n---\n\n"
            if not target_repo:
                target_repo = extract_target_repo(body)

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
You are an AgentSpec SDD build executor working inside a GitHub issue.

Based on the full specification below, generate ALL the files needed for this feature.

IMPORTANT: Respond with ONLY a valid JSON object in this exact format — no markdown, no explanation, just the JSON:

{{
  "branch": "feat/short-feature-name",
  "pr_title": "feat: short description",
  "pr_body": "## Summary\\n\\n- bullet 1\\n- bullet 2\\n\\nCloses #{issue_number}",
  "build_summary": "2-3 sentence summary of what was built",
  "files": [
    {{
      "path": "relative/path/to/file.ext",
      "content": "full file content here"
    }}
  ]
}}

Rules:
- "branch" must start with feat/, fix/, or chore/
- "files" must contain ALL files needed — complete, production-ready content
- No placeholder content — every file must be fully implemented
- "pr_body" must reference the issue number: {issue_number}

Context:
{context}
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
    prompt = PROMPTS["build"].format(
        context=context,
        issue_number=ISSUE_NUMBER,
    )

    print("Calling Claude for build spec...")
    raw = call_claude(prompt, max_tokens=8192)

    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())

    try:
        spec = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude did not return valid JSON: {e}\n\nRaw:\n{raw[:500]}")

    branch = spec["branch"]
    pr_title = spec["pr_title"]
    pr_body = spec["pr_body"]
    files = spec["files"]
    build_summary = spec.get("build_summary", "")

    print(f"Target repo: {target_repo}")
    print(f"Branch: {branch}")
    print(f"Files to create: {len(files)}")

    default_branch = get_default_branch(target_repo)
    base_sha = get_branch_sha(target_repo, default_branch)
    create_branch(target_repo, branch, base_sha)

    for i, f in enumerate(files):
        print(f"  Creating {f['path']} ({i+1}/{len(files)})")
        create_file(
            target_repo,
            f["path"],
            f["content"],
            branch,
            f"feat: add {f['path']}",
        )
        time.sleep(0.3)  # avoid rate limiting

    pr_url = create_pr(target_repo, branch, default_branch, pr_title, pr_body)
    print(f"PR created: {pr_url}")

    file_list = "\n".join(f"- `{f['path']}`" for f in files)
    return (
        f"## 🔨 BUILD EXECUTED: {ISSUE_TITLE}\n\n"
        f"{build_summary}\n\n"
        f"### Files created ({len(files)})\n{file_list}\n\n"
        f"### Pull Request\n"
        f"➡️ **[{pr_title}]({pr_url})**\n\n"
        f"Review and merge the PR in `{target_repo}` to complete this phase."
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print(f"SDD phase: {PHASE} | Issue: #{ISSUE_NUMBER} | Repo: {REPO}")

    if PHASE not in PROMPTS:
        print(f"Unknown phase: {PHASE}. Valid: {list(PROMPTS.keys())}")
        sys.exit(1)

    context, target_repo = build_context()
    print(f"Target repo: {target_repo or 'not specified'}")

    footer = (
        f"\n\n---\n"
        f"*AgentSpec SDD — Phase **{PHASE_ICON.get(PHASE, '')} {PHASE.title()}** "
        f"| Label `{LABEL_NAME}` on issue #{ISSUE_NUMBER}*"
    )
    if target_repo:
        footer += f"\n*Target: [{target_repo}](https://github.com/{target_repo})*"

    if PHASE == "build":
        if not target_repo:
            post_comment(
                "❌ **Build failed:** No `Target Repo` found in this issue.\n\n"
                "Add a line like:\n```\n**Target Repo:** owner/repo\n```\n"
                "Then re-add the `sdd:build` label."
            )
            sys.exit(1)

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

        if PHASE == "ship":
            close_issue()

    print("Done.")


if __name__ == "__main__":
    main()
