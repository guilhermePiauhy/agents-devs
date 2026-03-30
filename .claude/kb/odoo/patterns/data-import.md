# Pattern: CSV Import via XML-RPC

## When to Use

Use for controlled bulk imports when UI import is insufficient or needs repeatability.

## Input CSV

`data/customers.csv`

```csv
name,email,phone,country
John Doe,john@example.com,+1234567890,United States
Jane Smith,jane@example.com,+0987654321,Canada
```

## Script

`scripts/import_customers.py`

```python
#!/usr/bin/env python3
import csv
import os
import xmlrpc.client

url = os.getenv("ODOO_URL", "http://localhost:8069")
db = os.getenv("ODOO_DB")
username = os.getenv("ODOO_USERNAME")
password = os.getenv("ODOO_PASSWORD")

if not all([db, username, password]):
    raise ValueError("Set ODOO_DB, ODOO_USERNAME and ODOO_PASSWORD first.")

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})
if not uid:
    raise RuntimeError("Authentication failed.")

objects = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

with open("data/customers.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            country_name = (row.get("country") or "").strip()
            country_ids = objects.execute_kw(
                db,
                uid,
                password,
                "res.country",
                "search",
                [[["name", "=", country_name]]],
                {"limit": 1},
            ) if country_name else []

            objects.execute_kw(
                db,
                uid,
                password,
                "res.partner",
                "create",
                [{
                    "name": row["name"],
                    "email": row["email"],
                    "phone": row["phone"],
                    "country_id": country_ids[0] if country_ids else False,
                }],
            )
            print(f"Imported: {row['name']}")
        except Exception as exc:
            print(f"Failed: {row['name']} -> {exc}")
```

## Run

```bash
ODOO_DB=<db> ODOO_USERNAME=<user> ODOO_PASSWORD=<password> python scripts/import_customers.py
```
