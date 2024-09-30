# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Secondary Analytic Account",
    "version": "14.0.1.0.0",
    "category": "Account",
    "license": "AGPL-3",
    "author": "Akretion",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "depends": ["account"],
    "data": [
        "views/account_move_view.xml",
        "views/secondary_analytic_view.xml",
        "security/ir.model.access.csv",
        "security/analytic_security.xml",
    ],
    "installable": True,
}
