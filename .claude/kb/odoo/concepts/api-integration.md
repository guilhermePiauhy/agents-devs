# API and Integration

## Core Odoo API Access

Default endpoints:

```text
POST /xmlrpc/2/common
POST /xmlrpc/2/object
POST /jsonrpc
```

## XML-RPC Example

```python
import xmlrpc.client

url = "http://localhost:8069"
db = "my_db"
username = "admin@example.com"
password = "secret"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
objects = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
partners = objects.execute_kw(db, uid, password, "res.partner", "search_read", [[["is_company", "=", True]]])
```

## Outgoing Webhook Pattern

Odoo does not provide a universal outgoing webhook engine by default. A common approach is to trigger an HTTP call from model events.

```python
from odoo import api, models
import requests

class MyModel(models.Model):
    _name = "my.model"

    @api.model
    def create(self, vals):
        record = super().create(vals)
        requests.post(
            "https://external-app.example/webhooks/odoo",
            json={"event": "created", "id": record.id},
            timeout=10,
        )
        return record
```

## Integration Guidelines

- Keep credentials in environment or secure config.
- Add retry/error handling for external calls.
- Avoid blocking critical transactions with fragile network dependencies.
