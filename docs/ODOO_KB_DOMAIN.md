# Odoo KB Domain Documentation

> Knowledge base domain for Odoo ERP specialist agent. Contains 12 files across concepts and patterns for versions 14-17.

**Location:** `.claude/kb/odoo/` (in your agentspec repository)

**Files to Create:** 12 total
- 1x `index.md` (overview)
- 1x `quick-reference.md` (decision matrix)
- 6x `concepts/*.md` (theory)
- 4x `patterns/*.md` (implementation code)

---

## File 1: index.md

Create: `.claude/kb/odoo/index.md`

```markdown
# Odoo Knowledge Base

> Complete guide for Odoo ERP 14-17 implementation, configuration, and customization

## Overview

Odoo is an open-source ERP platform with:
- Modular architecture (core modules + custom modules)
- PostgreSQL database
- Python ORM (Object-Relational Mapping)
- XML-based UI definition
- Built-in workflow engine

## Topics by Category

### Core Concepts
- **Modules System** — Structure, manifest, initialization
- **Models & ORM** — Fields, inheritance, custom models
- **Views & UI** — Forms, trees, kanban, graph views
- **Security** — Access control, record rules, multi-company
- **Workflows** — State machines, automation, triggers
- **API & Integration** — REST endpoints, webhooks, connectors

### Patterns & Recipes
- Creating custom modules (folder structure, files)
- Building models + views step-by-step
- Data import strategies (CSV, APIs)
- Report generation (HTML, PDF)
- Custom workflows with business rules
- API integration (sending data, receiving events)

## Version Coverage

| Version | Release | EOL | Support |
|---------|---------|-----|---------|
| 17 | Oct 2023 | Oct 2025 | ✅ Full |
| 16 | Feb 2023 | Feb 2025 | ✅ Full |
| 15 | Feb 2022 | Feb 2024 | ⚠️ Maintenance |
| 14 | Feb 2021 | Feb 2023 | ❌ Expired |

## Quick Links

- [Concepts](./concepts/) — Core theory (6 files)
- [Patterns](./patterns/) — Working code examples (4 files)
- [Quick Reference](./quick-reference.md) — Decision tables

## Common Tasks

| Task | See File |
|------|----------|
| Start new Odoo project | concepts/modules-system.md |
| Build custom module | patterns/custom-modules.md |
| Import CSV data | patterns/data-import.md |
| Create report | patterns/reports.md |
| Setup workflows | concepts/workflows.md |

---
```

---

## File 2: quick-reference.md

Create: `.claude/kb/odoo/quick-reference.md`

```markdown
# Odoo Quick Reference

## Version Decision Matrix

**Which Odoo version should I use?**

| Need | v14 | v15 | v16 | v17 |
|------|-----|-----|-----|-----|
| Latest features | ❌ | ⚠️ | ✅ | ✅ |
| Stable (long-term) | ⚠️ | ⚠️ | ✅ | ❌ |
| Performance tuned | ❌ | ⚠️ | ✅ | ✅ |
| Community support | ❌ | ⚠️ | ✅ | ✅ |
| Security patches | ❌ | ❌ | ✅ | ✅ |

**Recommendation:** Use **v16 or v17** for new projects

## Module Structure Checklist

Essential files for any custom module:

```
my_module/
├── __manifest__.py       ← Module metadata (name, version, dependencies)
├── __init__.py          ← Python package initialization
├── models/
│   ├── __init__.py
│   └── my_model.py      ← Model definitions (tables + fields)
├── views/
│   ├── my_model_list.xml      ← List/tree view
│   ├── my_model_form.xml      ← Form view
│   └── my_model_kanban.xml    ← Kanban view (optional)
├── security/
│   └── ir.model.access.csv    ← Access control
└── data/
    └── data.xml         ← Sample data (optional)
```

## Model Field Types (Python)

```python
from odoo import models, fields

class MyModel(models.Model):
    _name = 'my.model'

    # Basic fields
    name = fields.Char("Name", required=True)
    description = fields.Text("Description")
    date = fields.Date("Date", default=fields.Date.today)
    amount = fields.Float("Amount", digits=(12, 2))
    active = fields.Boolean("Active", default=True)

    # Relationship fields
    partner_id = fields.Many2one('res.partner', "Partner")
    line_ids = fields.One2many('my.model.line', 'model_id', "Lines")
    tags = fields.Many2many('my.tag', "Tags")

    # Computed fields
    total = fields.Float(compute="_compute_total")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], default='draft')

    def _compute_total(self):
        for record in self:
            record.total = sum(line.amount for line in record.line_ids)
```

## Core API Access (XML-RPC / JSON-RPC)

```text
# Odoo core API endpoints (available by default)
POST /xmlrpc/2/common   # authentication and metadata
POST /xmlrpc/2/object   # model method calls (search, read, create, write, unlink)
POST /jsonrpc           # JSON-RPC alternative endpoint
```

> Note: Generic REST routes like `/api/resource/...` are not part of default Odoo Community/Enterprise.
> Use XML-RPC/JSON-RPC, or implement custom REST controllers/modules when needed.

## Security Record Rules

```xml
<!-- In security/ir.model.access.csv -->
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,My Model / User,model_my_model,group_user,1,0,0,0
access_my_model_manager,My Model / Manager,model_my_model,group_erp_manager,1,1,1,1
```

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Module ... not installed` | Missing dependency | Add to `__manifest__.py` depends |
| `AccessError` | No permission | Check record rules in security/ |
| `ProgrammingError: column does not exist` | Database not migrated | Run DB update: `odoo -d dbname -u my_module` |
| `ValidationError` | Field validation failed | Check field constraints |
| `RecursionError` | Infinite loop in compute | Add `@api.depends()` decorator |

---
```

---

## Files 3-8: Concepts (6 files in `concepts/` directory)

### concepts/modules-system.md

```markdown
# Odoo Modules System

## Module Anatomy

A module is a Python package with metadata:

**__manifest__.py** — Module definition
```python
{
    'name': 'My Custom Module',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'author': 'Company Name',
    'license': 'LGPL-3',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
}
```

## Installation Flow

1. User uploads module to `.addons/` folder
2. Odoo scans `__manifest__.py`
3. Creates tables for models
4. Loads security rules
5. Registers views
6. Ready to use

## Module Dependencies

- `base` — Core Odoo (never skip)
- `sale` — Sales module
- `purchase` — Purchases
- `inventory` — Stock
- etc.

Circular dependencies cause errors!

---
```

### concepts/models-orm.md

```markdown
# Models & ORM (Odoo Object-Relational Mapping)

## What is a Model?

A model = Database table + Python class

```python
class MyModel(models.Model):
    _name = 'my.model'  # Database table identifier
    _description = 'My Custom Model'

    name = fields.Char("Name")
```

Creates: Table `my_model` with columns `id, name`

## Inheritance Types

### Single Inheritance
```python
class ExtendedModel(models.Model):
    _inherit = 'res.partner'  # Extends existing model

    custom_field = fields.Char("Custom Field")
```

New fields added to `res_partner` table.

### Multiple Inheritance
```python
class MixinFields(models.AbstractModel):
    _name = 'my.mixin'

    created_by = fields.Many2one('res.users')

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = 'my.mixin'

    name = fields.Char("Name")
```

---
```

### concepts/views-ui.md

```markdown
# Views & User Interface

## View Types

```xml
<!-- Form View - Data entry -->
<form>
    <sheet>
        <h1><field name="name"/></h1>
        <group>
            <field name="partner_id"/>
            <field name="amount"/>
        </group>
    </sheet>
</form>

<!-- Tree (List) View -->
<tree>
    <field name="name"/>
    <field name="partner_id"/>
    <field name="amount" sum="Total"/>
</tree>

<!-- Kanban View (cards) -->
<kanban>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <div t-esc="record.name"/>
            </div>
        </t>
    </templates>
</kanban>

<!-- Graph View (charts) -->
<graph type="column">
    <field name="partner_id" type="row"/>
    <field name="amount" type="measure"/>
</graph>
```

## Actions (Menu Items)

```xml
<action
    name="My Documents"
    type="ir.actions.act_window"
    res_model="my.model"
    view_mode="kanban,tree,form"
    domain="[('state', '=', 'open')]"
/>
```

---
```

### concepts/security.md

```markdown
# Security Model

## Access Control List (ACL)

File: `security/ir.model.access.csv`

Columns:
- `id` — unique identifier
- `name` — human readable name
- `model_id:id` — model reference
- `group_id:id` — group this applies to
- `perm_read, perm_write, perm_create, perm_unlink` — 0 or 1

Example:
```
access_order_user,Order / User,sale.model_order,group_sale_user,1,1,1,0
```

Means: Sales users can READ + WRITE + CREATE orders, but NOT delete.

## Record Rules (Row-Level Security)

```xml
<record model="ir.rule" id="my_rule">
    <field name="name">My Documents Only</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">
        [('user_id', '=', user.id)]
    </field>
    <field name="perm_read" eval="1"/>
    <field name="perm_write" eval="1"/>
    <field name="perm_create" eval="0"/>
</record>
```

Restricts users to seeing only their own records.

---
```

### concepts/workflows.md

```markdown
# Workflows & Automation

## State Machines

```python
class MyModel(models.Model):
    _name = 'my.model'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], default='draft')

    def action_confirm(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError("Can only confirm draft records")
            record.state = 'confirmed'

    def action_done(self):
        self.state = 'done'
```

## Automated Actions

```xml
<!-- Auto-send email when state = done -->
<record model="ir.automation" id="auto_email">
    <field name="name">Send Email on DONE</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="trigger">on_change</field>
    <field name="state_field_id" ref="field_my_model_state"/>
    <field name="trigger_value">done</field>
    <field name="action_server_id" ref="ir_actions_server_send_email"/>
</record>
```

---
```

### concepts/api-integration.md

```markdown
# API & Integration

## Webhook Pattern (Custom Implementation)

```python
from odoo import api, models
import requests

class MyModel(models.Model):
    _name = 'my.model'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        # Odoo does not provide a generic outgoing webhook engine by default.
        # Typical pattern: trigger HTTP call from model/business event.
        requests.post(
            'https://external-app.com/webhooks/odoo',
            json={'action': 'created', 'id': record.id},
            timeout=10
        )
        return record
```

## External API Calls

```python
def action_sync_with_crm(self):
    import requests

    for record in self:
        response = requests.post(
            'https://crm.example.com/api/contacts',
            json={
                'name': record.name,
                'email': record.email,
            },
            headers={'Authorization': f'Bearer {self.env.company.api_token}'}
        )

        if response.status_code == 201:
            record.crm_id = response.json()['id']
```

---
```

---

## Files 9-12: Patterns (4 files in `patterns/` directory)

### patterns/custom-modules.md

```markdown
# Creating Custom Modules - Step by Step

## Project Layout

```
odoo-project/
├── odoo/
│   └── addons/
│       └── my_module/                 ← YOUR MODULE
│           ├── __manifest__.py
│           ├── __init__.py
│           ├── models/
│           │   ├── __init__.py
│           │   └── my_model.py
│           ├── views/
│           │   └── my_views.xml
│           ├── security/
│           │   └── ir.model.access.csv
│           └── data/
│               └── demo_data.xml
├── docker-compose.yml
└── .env
```

## Step 1: Create Module Structure

```bash
mkdir -p odoo/addons/my_module/models
mkdir -p odoo/addons/my_module/views
mkdir -p odoo/addons/my_module/security
mkdir -p odoo/addons/my_module/data
```

## Step 2: Create __manifest__.py

```python
{
    'name': 'My Module',
    'version': '17.0.1.0.0',
    'category': 'Tools',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/my_views.xml',
    ],
    'installable': True,
}
```

## Step 3: Create Model

`models/my_model.py`:
```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Custom Model'

    name = fields.Char("Name", required=True)
    description = fields.Text("Description")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')])

    @api.model
    def create(self, vals):
        record = super().create(vals)
        return record
```

`models/__init__.py`:
```python
from . import my_model
```

## Step 4: Install in Odoo

```bash
docker compose exec odoo bash
# Inside container:
odoo -d {dbname} -u my_module
```

---
```

### patterns/models-views.md

```markdown
# Building Models + Views Together

## Example: Project Management Module

### 1. Model Definition

`models/project.py`:
```python
class Project(models.Model):
    _name = 'project.project'
    _description = 'Project'

    name = fields.Char("Project Name", required=True)
    manager_id = fields.Many2one('res.users', "Manager")
    task_ids = fields.One2many('project.task', 'project_id', "Tasks")
    status = fields.Selection([
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('done', 'Done'),
    ], default='planning')

    task_count = fields.Integer(compute="_compute_task_count")

    def _compute_task_count(self):
        for project in self:
            project.task_count = len(project.task_ids)

class ProjectTask(models.Model):
    _name = 'project.task'
    _description = 'Project Task'

    name = fields.Char("Task", required=True)
    project_id = fields.Many2one('project.project', "Project")
    assigned_to = fields.Many2one('res.users', "Assigned To")
    status = fields.Selection([
        ('todo', 'To Do'),
        ('inprogress', 'In Progress'),
        ('done', 'Done'),
    ], default='todo')
```

### 2. Views

`views/project_views.xml`:
```xml
<?xml version="1.0"?>
<odoo>
    <!-- Project List -->
    <record model="ir.ui.view" id="project_tree">
        <field name="name">Projects</field>
        <field name="model">project.project</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="manager_id"/>
                <field name="status"/>
                <field name="task_count"/>
            </tree>
        </field>
    </record>

    <!-- Project Form -->
    <record model="ir.ui.view" id="project_form">
        <field name="name">Project</field>
        <field name="model">project.project</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <h1><field name="name"/></h1>
                    <group>
                        <field name="manager_id"/>
                        <field name="status"/>
                    </group>
                    <notebook>
                        <page string="Tasks">
                            <field name="task_ids">
                                <tree editable="bottom">
                                    <field name="name"/>
                                    <field name="assigned_to"/>
                                    <field name="status"/>
                                </tree>
                            </field>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>

    <!-- Action -->
    <record model="ir.actions.act_window" id="project_action">
        <field name="name">Projects</field>
        <field name="res_model">project.project</field>
        <field name="view_mode">kanban,tree,form</field>
    </record>

    <!-- Menu -->
    <menuitem
        name="Projects"
        id="project_menu_root"
        action="project_action"
        sequence="10"
    />
</odoo>
```

---
```

### patterns/data-import.md

```markdown
# Data Import - CSV to Odoo

## Step 1: Prepare CSV

`data/customers.csv`:
```
name,email,phone,country_id
John Doe,john@example.com,+1234567890,United States
Jane Smith,jane@example.com,+0987654321,Canada
```

## Step 2: Import Script

`scripts/import_customers.py`:
```python
#!/usr/bin/env python3
import csv
import os
import xmlrpc.client

# Odoo connection
url = os.getenv('ODOO_URL', 'http://localhost:8069')
db = os.getenv('ODOO_DB')
username = os.getenv('ODOO_USERNAME')
password = os.getenv('ODOO_PASSWORD')

if not all([db, username, password]):
    raise ValueError("Set ODOO_DB, ODOO_USERNAME, and ODOO_PASSWORD before running.")

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
objects = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Login
uid = common.authenticate(db, username, password, {})
if not uid:
    raise RuntimeError("Authentication failed. Check Odoo credentials.")

# Read CSV
with open('data/customers.csv', newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            country_name = (row.get('country_id') or '').strip()
            country_ids = objects.execute_kw(
                db, uid, password,
                'res.country', 'search',
                [[['name', '=', country_name]]],
                {'limit': 1}
            ) if country_name else []

            objects.execute_kw(db, uid, password, 'res.partner', 'create', [{
                'name': row['name'],
                'email': row['email'],
                'phone': row['phone'],
                'country_id': country_ids[0] if country_ids else False,
            }])
            print(f"✓ Imported: {row['name']}")
        except Exception as e:
            print(f"✗ Failed: {row['name']} - {e}")
```

## Step 3: Run Import

```bash
docker compose exec odoo python scripts/import_customers.py
```

---
```

### patterns/reports.md

```markdown
# Generating Reports

## Report Definition

`models/report.py`:
```python
from odoo import api, models, fields

class ProjectReport(models.AbstractModel):
    _name = 'report.my_module.project_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        projects = self.env['project.project'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'project.project',
            'docs': projects,
            'data': data,
        }
```

## Report Template (QWeb)

`views/report_templates.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="project_report">
        <t t-call="web.html_container">
            <div class="header">
                <h1>Project Report</h1>
            </div>
            <t t-foreach="docs" t-as="project">
                <div class="page">
                    <h2><t t-esc="project.name"/></h2>
                    <table class="table table-bordered">
                        <tr>
                            <th>Task</th>
                            <th>Status</th>
                            <th>Assigned</th>
                        </tr>
                        <t t-foreach="project.task_ids" t-as="task">
                            <tr>
                                <td><t t-esc="task.name"/></td>
                                <td><t t-esc="task.status"/></td>
                                <td><t t-esc="task.assigned_to.name"/></td>
                            </tr>
                        </t>
                    </table>
                </div>
            </t>
        </t>
    </template>

    <!-- Report Definition -->
    <report
        id="project_report_action"
        model="project.project"
        string="Project Report"
        report_type="qweb-pdf"
        name="my_module.project_report"
        file="my_module.project_report"
    />
</odoo>
```

---
```

### patterns/custom-workflows.md (reusing workflows.md content for completeness)

Already covered in concepts/workflows.md section.

---

## Validation Checklist

### ✅ Odoo KB Domain Complete When:

- [ ] `.claude/kb/odoo/` directory created
- [ ] `index.md` — overview with 6 topics ✓
- [ ] `quick-reference.md` — decision matrices ✓
- [ ] 6 concept files in `concepts/`:
  - [ ] modules-system.md
  - [ ] models-orm.md
  - [ ] views-ui.md
  - [ ] security.md
  - [ ] workflows.md
  - [ ] api-integration.md
- [ ] 4 pattern files in `patterns/`:
  - [ ] custom-modules.md
  - [ ] models-views.md
  - [ ] data-import.md
  - [ ] reports.md
- [ ] All files accessible from agent via KB search

### How to Implement

```bash
# Create directory
mkdir -p .claude/kb/odoo/concepts .claude/kb/odoo/patterns

# Copy files from this document
# Save each section as appropriate .md file

# Test: Verify agent can load
# Run: /build with Odoo DESIGN document
```

---

**Status:** Ready for your validation & file creation
- [ ] Review all 12 file descriptions
- [ ] Create the 12 files in `.claude/kb/odoo/`
- [ ] Test with `odoo-specialist` agent reference
