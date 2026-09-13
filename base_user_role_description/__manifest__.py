# Copyright 2025 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Base User Role Description",
    "summary": "Add short description to user roles by accesses and menus",
    "version": "14.0.1.0.0",
    "category": "tools",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "maintainers": ["Kev-Roche"],
    "application": False,
    "installable": True,
    "depends": [
        "base_user_role",
    ],
    "data": [
        "views/res_users.xml",
        "views/res_users_role.xml",
        "data/cron.xml",
    ],
}
