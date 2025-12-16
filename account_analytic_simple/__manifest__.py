# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Analytic Simple",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "summary": "Add analytic account on account move line",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "license": "AGPL-3",
    "depends": [
        "account",
    ],
    "data": [
        "security/analytic_security.xml",
        "security/ir.model.access.csv",
        "views/account_move.xml",
        "views/account_move_line.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
