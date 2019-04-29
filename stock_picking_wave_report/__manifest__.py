# -*- coding: utf-8 -*-
# © 2013-2017 Odoo SA
# © 2018 Pierrick Brun <pierrick.brun@akretion.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Stock Picking Wave Report",
    "version": "10.0.1.0.0",
    "category": "Warehouse",
    "author": "Odoo SA, Akretion, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "depends": ["stock_picking_wave"],
    "data": [
        "report/stock_picking_wave_report_views.xml",
        "report/report_picking_wave.xml",
    ],
    "installable": True,
}
