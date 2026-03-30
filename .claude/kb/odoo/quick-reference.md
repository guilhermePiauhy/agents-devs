# Odoo Quick Reference

## Version Decision Matrix

| Need | v14 | v15 | v16 | v17 |
|------|-----|-----|-----|-----|
| New implementation | No | Caution | Yes | Yes |
| Long-term stability | No | Caution | Yes | Caution |
| Community activity | Low | Medium | High | High |
| Security posture (new deployments) | No | Caution | Yes | Yes |

## Module Skeleton

```text
my_module/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── my_model_views.xml
├── security/
│   └── ir.model.access.csv
└── data/
    └── demo.xml (optional)
```

## Core API Endpoints

```text
POST /xmlrpc/2/common
POST /xmlrpc/2/object
POST /jsonrpc
```

## Common Commands

```bash
# Update one module
odoo -d <db_name> -u my_module

# Update all modules
odoo -d <db_name> -u all
```

## Frequent Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Module not found` | addon path/dependency issue | Check addons path and `depends` |
| `AccessError` | missing ACL/rule | Review `security/` files |
| `column does not exist` | DB not migrated | Run module update with `-u` |
| `ValidationError` | invalid field/domain logic | Validate constraints and input |
