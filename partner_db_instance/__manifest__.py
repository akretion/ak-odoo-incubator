{
    "name": "Partner DB Instance",
    "version": "18.0.1.0.0",
    "summary": "Manage and create on the fly odoo partner instances",
    "depends": ["contacts"],
    "external_dependencies": {
        "python": ["pyjwt"],
    },
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "data": [
        "security/res_groups.xml",
        "security/res_partner_instance.xml",
        "views/res_partner_views.xml",
        "views/res_partner_instance_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
