# Copyright 2023 Akretion (https://www.akretion.com).
# @author Chafique Delli <chafique.delli@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "POS Custom Report Session",
    "version": "14.0.1.0.0",
    "category": "Point Of Sale",
    "author": "Akretion",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "license": "AGPL-3",
    "depends": [
        "pos_report_session_summary",
        "pos_sale_order",
    ],
    "data": [
        "views/report_session_summary.xml",
    ],
    "qweb": [],
    "installable": True,
}
