# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "MRP Propagate Lot",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "license": "AGPL-3",
    "depends": [
        "mrp",
        "sale_order_lot_generator",
    ],
    "data": ["views/mrp_production_views.xml"],
    "installable": True,
}
