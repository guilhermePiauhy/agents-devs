# Odoo Modules System

## What Is a Module

A module is a Python package with metadata (`__manifest__.py`) loaded by Odoo to register models, views, security, data, and reports.

## Manifest Essentials

```python
{
    "name": "My Module",
    "version": "17.0.1.0.0",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/my_model_views.xml",
    ],
    "installable": True,
}
```

## Lifecycle

1. Odoo scans addons path
2. Reads manifest and dependencies
3. Loads models and DB metadata
4. Applies security and views
5. Module becomes available in Apps

## Key Rules

- Keep manifests explicit and minimal.
- Declare dependencies correctly.
- Avoid circular dependencies.
