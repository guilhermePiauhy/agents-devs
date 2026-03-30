# Pattern: Models + Views Together

## Goal

Implement a model and expose it in Odoo UI in one coherent step.

## Model

`models/project_item.py`

```python
from odoo import models, fields

class ProjectItem(models.Model):
    _name = "project.item"
    _description = "Project Item"

    name = fields.Char(required=True)
    owner_id = fields.Many2one("res.users", string="Owner")
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("done", "Done")],
        default="draft",
    )
```

## Views + Action + Menu

`views/project_item_views.xml`

```xml
<odoo>
    <record id="view_project_item_tree" model="ir.ui.view">
        <field name="name">project.item.tree</field>
        <field name="model">project.item</field>
        <field name="arch" type="xml">
            <tree>
                <field name="name"/>
                <field name="owner_id"/>
                <field name="state"/>
            </tree>
        </field>
    </record>

    <record id="view_project_item_form" model="ir.ui.view">
        <field name="name">project.item.form</field>
        <field name="model">project.item</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="owner_id"/>
                        <field name="state"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_project_item" model="ir.actions.act_window">
        <field name="name">Project Items</field>
        <field name="res_model">project.item</field>
        <field name="view_mode">tree,form</field>
    </record>

    <menuitem id="menu_project_item_root" name="Project Items" action="action_project_item"/>
</odoo>
```
