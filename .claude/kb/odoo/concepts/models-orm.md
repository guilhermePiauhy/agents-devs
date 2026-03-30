# Models and ORM

## Model Basics

Every Odoo model maps to a database table and business behavior layer.

```python
from odoo import models, fields

class MyModel(models.Model):
    _name = "my.model"
    _description = "My Model"

    name = fields.Char(required=True)
    amount = fields.Float()
```

## Common Relationships

- `Many2one`: child -> parent
- `One2many`: parent -> children
- `Many2many`: many-to-many link

## Inheritance Patterns

- `_inherit`: extend existing model
- `_name` + `_inherit`: create delegated/customized model behavior
- `AbstractModel`: reusable mixins

## ORM Good Practices

- Prefer ORM methods (`search`, `create`, `write`, `unlink`) over raw SQL.
- Use `@api.depends` for computed fields.
- Keep business validations near model methods.
