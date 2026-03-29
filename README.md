<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner.svg">
  <source media="(prefers-color-scheme: light)" srcset="assets/banner.svg">
  <img alt="AgentSpec — Spec-Driven Data Engineering" src="assets/banner.svg" width="100%">
</picture>

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-blueviolet.svg)](plugin/)
[![Version](https://img.shields.io/badge/version-3.0.0-green.svg)](CHANGELOG.md)
[![Agents](https://img.shields.io/badge/agents-58-orange.svg)](.claude/agents/)
[![KB Domains](https://img.shields.io/badge/KB%20domains-22-blue.svg)](.claude/kb/)
[![Commands](https://img.shields.io/badge/commands-29-brightgreen.svg)](.claude/commands/)

**A single AI agent reviewing your pipeline will miss things.<br/>58 specialized agents debating your pipeline will catch them.**

[Install](#install) | [Quick Start](#quick-start) | [Commands](#which-command-do-i-need) | [Documentation](docs/) | [Contributing](CONTRIBUTING.md)

</div>

---

## Why AgentSpec?

Data engineering with AI assistants produces inconsistent results: hallucinated SQL, wrong partition strategies, missing quality checks, and pipelines that work in dev but break in production. Each conversation starts from scratch without accumulated domain knowledge.

**AgentSpec fixes this.** It's a Claude Code plugin that gives every session access to 22 knowledge base domains, 58 specialized agents, and a 5-phase workflow that turns vague requirements into production-ready data pipelines — with quality gates at every step.

```text
/brainstorm  →  /define  →  /design  →  /build  →  /ship
  (Explore)    (Capture)   (Architect)  (Execute)  (Archive)
       │            │            │            │
  Compare      Data Contract  Pipeline    dbt build
  approaches   Schema SLAs    DAG Design  sqlfluff lint
               Source Inventory Partitions  GE suite run
```

Every phase understands data engineering context: source inventories, freshness SLAs, schema contracts, partition strategies, and data quality gates.

---

## Install

### Plugin (Recommended)

```bash
# Add the AgentSpec marketplace and install
claude plugin marketplace add luanmorenommaciel/agentspec
claude plugin install agentspec
```

That's it. Every Claude Code session now has AgentSpec. Updates are one command:

```bash
claude plugin update agentspec
```

### Local Testing

```bash
git clone https://github.com/luanmorenommaciel/agentspec.git
claude --plugin-dir ./agentspec/plugin
```

### Legacy (Copy)

```bash
git clone https://github.com/luanmorenommaciel/agentspec.git
cp -r agentspec/.claude your-project/.claude
```

---

## Quick Start

### Build a Data Pipeline in 5 Steps

```bash
# 1. Explore the approach
/agentspec:brainstorm "Daily orders pipeline from Postgres to Snowflake star schema"

# 2. Capture requirements with data contracts
/agentspec:define ORDERS_PIPELINE

# 3. Design the pipeline architecture (DAG, partitions, incremental strategy)
/agentspec:design ORDERS_PIPELINE

# 4. Build with dbt + quality verification
/agentspec:build ORDERS_PIPELINE

# 5. Archive with lessons learned
/agentspec:ship ORDERS_PIPELINE
```

### Or Jump Straight to What You Need

```bash
/agentspec:schema "Star schema for e-commerce analytics"
/agentspec:pipeline "Daily orders ETL from Postgres to Snowflake"
/agentspec:data-quality models/staging/stg_orders.sql
/agentspec:sql-review models/marts/
```

---

## Which Command Do I Need?

### Data Engineering

| I want to... | Command | Agent |
|---|---|---|
| Design a data pipeline / DAG | `/agentspec:pipeline` | pipeline-architect |
| Design a star schema / data model | `/agentspec:schema` | schema-designer |
| Add data quality checks | `/agentspec:data-quality` | data-quality-analyst |
| Optimize slow SQL | `/agentspec:sql-review` | sql-optimizer |
| Choose Iceberg vs Delta Lake | `/agentspec:lakehouse` | lakehouse-architect |
| Build a RAG / embedding pipeline | `/agentspec:ai-pipeline` | ai-data-engineer |
| Create a data contract | `/agentspec:data-contract` | data-contracts-engineer |
| Migrate legacy SSIS / Informatica | `/agentspec:migrate` | dbt-specialist + spark-engineer |

### SDD Workflow

| I want to... | Command | What Happens |
|---|---|---|
| Explore an idea | `/agentspec:brainstorm` | Compare approaches, ask discovery questions |
| Capture requirements | `/agentspec:define` | Structured requirements with clarity score |
| Design architecture | `/agentspec:design` | File manifest + pipeline architecture |
| Implement the feature | `/agentspec:build` | Auto-delegates to specialist agents |
| Archive completed work | `/agentspec:ship` | Lessons learned + metrics |
| Update after changes | `/agentspec:iterate` | Cascade-aware doc updates |

### Visual & Utilities

| I want to... | Command |
|---|---|
| Generate architecture diagrams | `/agentspec:generate-web-diagram` |
| Create slide decks | `/agentspec:generate-slides` |
| Review code | `/agentspec:review` |
| Analyze meeting notes | `/agentspec:meeting` |
| Create a new KB domain | `/agentspec:create-kb` |

---

## How It Works

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  BRAINSTORM  │────▶│    DEFINE    │────▶│    DESIGN    │
│  Data Flow   │     │ Data Contract│     │ Pipeline Arch│
│  Sketch      │     │ Schema SLAs  │     │ DAG + Parts  │
└──────────────┘     └──────────────┘     └──────────────┘
                                               │
                     ┌─────────────────────────┼─────────────────────────┐
                     ▼                         ▼                         ▼
              ┌────────────┐           ┌────────────┐           ┌────────────┐
              │ dbt-spec   │           │ spark-eng  │           │ pipeline   │
              │ Models     │           │ Jobs       │           │ DAGs       │
              └─────┬──────┘           └─────┬──────┘           └─────┬──────┘
                    └────────────────────────┼─────────────────────────┘
                                             ▼
                                      ┌────────────┐
                                      │   BUILD    │
                                      │ dbt build  │
                                      │ sqlfluff   │
                                      │ GE suite   │
                                      └─────┬──────┘
                                             ▼
                                      ┌────────────┐
                                      │    SHIP    │
                                      │  Archive   │
                                      └────────────┘
```

**Agent matching:** Your DESIGN doc specifies dbt staging models, a PySpark job, and an Airflow DAG — AgentSpec automatically delegates to `dbt-specialist`, `spark-engineer`, and `pipeline-architect`.

**Requirements changed?** `/agentspec:iterate` updates any phase document with automatic cascade detection to downstream docs.

---

## 58 Agents Across 8 Categories

| Category | Count | What They Do |
|----------|-------|---|
| **Workflow** | 6 | Drive the 5-phase SDD lifecycle |
| **Architect** | 8 | Schema design, pipeline architecture, medallion layers, GenAI systems |
| **Data Engineering** | 15 | dbt, Spark, Airflow, streaming, Lakeflow, SQL optimization |
| **Cloud** | 10 | AWS Lambda, GCP Cloud Run, Supabase, CI/CD, Terraform |
| **Platform** | 6 | Microsoft Fabric (architecture, pipelines, security, AI, logging, CI/CD) |
| **Python** | 6 | Code review, documentation, cleaning, prompt engineering |
| **Dev** | 4 | Codebase exploration, shell scripting, meeting analysis |
| **Test** | 3 | Test generation, data quality, data contracts |

Every agent follows the same cognitive framework: **KB-first knowledge resolution** with confidence scoring, explicit escalation rules, and quality gates.

---

## 22 Knowledge Base Domains

| Category | Domains |
|----------|---------|
| **Core DE** | `dbt` `spark` `sql-patterns` `airflow` `streaming` |
| **Data Design** | `data-modeling` `data-quality` `medallion` |
| **Infrastructure** | `lakehouse` `lakeflow` `cloud-platforms` `terraform` |
| **Cloud** | `aws` `gcp` `microsoft-fabric` |
| **AI & Modern** | `ai-data-engineering` `modern-stack` `genai` `prompt-engineering` |
| **Foundations** | `pydantic` `python` `testing` |

Agents consult KB domains before responding. When local knowledge is insufficient, they fall back to MCP tools — but KB is always checked first.

---

## 5-Phase Workflow with Quality Gates

| Phase | Command | Output | Gate |
|-------|---------|--------|------|
| **0. Brainstorm** | `/agentspec:brainstorm` | `BRAINSTORM_{FEATURE}.md` | 3+ questions, 2+ approaches |
| **1. Define** | `/agentspec:define` | `DEFINE_{FEATURE}.md` | Clarity Score >= 12/15 |
| **2. Design** | `/agentspec:design` | `DESIGN_{FEATURE}.md` | Complete manifest + schema plan |
| **3. Build** | `/agentspec:build` | Code + `BUILD_REPORT_{FEATURE}.md` | All tests pass |
| **4. Ship** | `/agentspec:ship` | `SHIPPED_{DATE}.md` | Acceptance verified |

---

## Project Structure

```text
agentspec/
├── .claude/                 # Source of truth (58 agents, 29 commands, 22 KB)
│   ├── agents/              # 8 categories of specialized agents
│   ├── commands/            # SDD + DE + visual + core commands
│   ├── skills/              # visual-explainer, excalidraw-diagram
│   ├── kb/                  # 22 knowledge base domains
│   └── sdd/                 # Templates, contracts, features, archive
│
├── plugin/                  # Distributable Claude Code plugin
│   ├── .claude-plugin/      # Manifest + marketplace config
│   ├── agents/              # Path-rewritten agents
│   ├── commands/            # Path-rewritten commands
│   ├── skills/              # 4 skills (2 original + 2 plugin-only)
│   ├── kb/                  # Knowledge base domains
│   ├── hooks/               # SessionStart workspace init
│   └── scripts/             # Initialization scripts
│
├── plugin-extras/           # Plugin-only content (merged by build)
├── build-plugin.sh          # Packages .claude/ into plugin/
├── docs/                    # Getting started, concepts, tutorials, reference
└── README.md
```

---

## Documentation

| Guide | Description |
|-------|-------------|
| [Getting Started](docs/getting-started/) | Install and build your first data pipeline |
| [Core Concepts](docs/concepts/) | SDD pillars through a data engineering lens |
| [Tutorials](docs/tutorials/) | dbt, star schema, data quality, Spark, streaming, RAG |
| [Reference](docs/reference/) | Full catalog: 58 agents, 29 commands, 22 KB domains |

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

- **New Agents** — add specialized agents for your domain
- **KB Domains** — share knowledge base domains
- **Commands** — new slash commands for data workflows
- **Plugin Development** — improve the build pipeline and distribution

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**[Documentation](docs/) | [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md)**

Built with [Claude Code](https://docs.anthropic.com/en/docs/claude-code)

</div>
