# Views and UI

## View Types

- `form`: create/edit a single record
- `tree` (list): tabular overview
- `kanban`: card-based status workflows
- `search`: filters and group-by behavior
- `graph`/`pivot`: reporting and analytics

## Minimal View Example

```xml
<record id="my_model_view_tree" model="ir.ui.view">
    <field name="name">my.model.tree</field>
    <field name="model">my.model</field>
    <field name="arch" type="xml">
        <tree>
            <field name="name"/>
            <field name="amount"/>
        </tree>
    </field>
</record>
```

## Navigation

Use actions + menuitems to expose models in UI:

- `ir.actions.act_window` defines target model and view modes
- `menuitem` connects action into navigation tree

## Best Practices

- Keep views modular and readable.
- Avoid heavy business logic in XML domains where Python is clearer.
