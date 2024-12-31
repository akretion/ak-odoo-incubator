# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Last Price",
    "summary": """
        Display on sale order lines the last sale price coming from an old system
        for control during a migration
    """,
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order.xml",
        "views/history.xml",
    ],
}
