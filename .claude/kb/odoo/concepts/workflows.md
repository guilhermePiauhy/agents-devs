# Workflows and Automation

## State Machine Pattern

Use a `Selection` field and explicit transition methods.

```python
from odoo import models, fields
from odoo.exceptions import ValidationError

class MyModel(models.Model):
    _name = "my.model"

    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("done", "Done"), ("cancel", "Cancelled")],
        default="draft",
    )

    def action_confirm(self):
        for record in self:
            if record.state != "draft":
                raise ValidationError("Only draft records can be confirmed.")
            record.state = "confirmed"
```

## Automation Options

- Server actions (`ir.actions.server`)
- Automated actions (`base.automation`)
- Scheduled jobs (`ir.cron`)

## Guidance

- Keep transitions explicit and auditable.
- Validate preconditions before each state change.
- Prefer idempotent automation where possible.
