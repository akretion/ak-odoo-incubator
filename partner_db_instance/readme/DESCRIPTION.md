This module allows a master odoo instance to manage multiple partner odoo databases.

Configuration
=============

To configure this module, you need to set the following parameters in your odoo configuration file:

```
[options]
dbfilter = ^project_%d$
partner_db_instance_master = project_base
partner_db_instance_password = your_complex_password
partner_db_instance_modules = db_instance,...
list_db = False
```

The dbfilter parameter specifies the naming convention for the partner databases and associate the partner subdomains with the partner database.

The `base` subdomain specified in `partner_db_instance_master` will be the master site from which all partner sites will be created.

To create a partner site, you need to click on the `Create Instance` button in the partner form.

You then need to `Deploy` the instance in the `Partner DB Instance` form.

Finally, you can connect to the partner site using the 'Connect' button in the same form once the instance is deployed. This will create a user corresponding to the current user in the partner instance.

Instances can be Archived and Redeployed without data loss.
