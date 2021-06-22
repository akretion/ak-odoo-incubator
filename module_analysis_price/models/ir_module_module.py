# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    code_qty = fields.Integer(
        string="Total Code Quantity (Python, xml, JS)",
        compute="_compute_code_qty",
        store=True,
    )

    def _compute_code_qty(self):
        for record in self:
            record.code_qty = (
                record.python_code_qty + record.xml_code_qty + record.js_code_qty
            )
