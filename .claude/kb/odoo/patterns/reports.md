# Pattern: QWeb PDF Report

## Goal

Generate printable PDF reports for a model with structured data.

## Report Model

`models/report_project_item.py`

```python
from odoo import api, models

class ReportProjectItem(models.AbstractModel):
    _name = "report.my_module.project_item_report"
    _description = "Project Item Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["project.item"].browse(docids)
        return {
            "doc_ids": docids,
            "doc_model": "project.item",
            "docs": docs,
            "data": data or {},
        }
```

## QWeb Template + Action

`views/report_project_item.xml`

```xml
<odoo>
    <template id="project_item_report_template">
        <t t-call="web.html_container">
            <t t-foreach="docs" t-as="doc">
                <div class="page">
                    <h2><t t-esc="doc.name"/></h2>
                    <p>Status: <t t-esc="doc.state"/></p>
                    <p>Owner: <t t-esc="doc.owner_id.name"/></p>
                </div>
            </t>
        </t>
    </template>

    <report
        id="project_item_report_action"
        model="project.item"
        string="Project Item Report"
        report_type="qweb-pdf"
        name="my_module.project_item_report_template"
        file="my_module.project_item_report_template"
    />
</odoo>
```

## Notes

- Keep report model lightweight.
- Use explicit field rendering to avoid accidental disclosure of sensitive data.
