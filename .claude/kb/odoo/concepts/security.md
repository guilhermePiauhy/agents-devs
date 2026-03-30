# Security

## Security Layers

1. **ACLs** (`ir.model.access.csv`) define model-level CRUD permissions.
2. **Record rules** (`ir.rule`) define row-level filtering.
3. **Groups** organize role-based access.

## ACL Example

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model user,model_my_model,base.group_user,1,0,0,0
access_my_model_manager,my.model manager,model_my_model,base.group_system,1,1,1,1
```

## Record Rule Example

```xml
<record id="my_model_own_records_rule" model="ir.rule">
    <field name="name">Own records only</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
</record>
```

## Security Guidelines

- Start restrictive, then open only what is needed.
- Review permissions in multi-company contexts.
- Avoid bypassing permissions in custom code unless truly required.
