# Pattern: Custom Module Scaffold

## When to Use

Use this when you need a new business capability in Odoo and want an installable addon structure.

## Step 1: Create Structure

```bash
mkdir -p odoo/addons/my_module/{models,views,security,data}
touch odoo/addons/my_module/__init__.py
touch odoo/addons/my_module/models/__init__.py
```

## Step 2: Manifest

`odoo/addons/my_module/__manifest__.py`

```python
{
    "name": "My Module",
    "version": "17.0.1.0.0",
    "summary": "Custom business module",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/my_model_views.xml",
    ],
    "installable": True,
}
```

## Step 3: Model

`odoo/addons/my_module/models/my_model.py`

```python
from odoo import models, fields

class MyModel(models.Model):
    _name = "my.model"
    _description = "My Model"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
```

`odoo/addons/my_module/models/__init__.py`

```python
from . import my_model
```

## Step 4: Install/Update

```bash
odoo -d <db_name> -u my_module
```
