# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    code_qty = fields.Integer(
        string="Total Code Quantity (Python, xml, JS)",
        compute="_compute_code_qty",
        store=True,
    )

    @api.depends("python_code_qty", "xml_code_qty", "js_code_qty")
    def _compute_code_qty(self):
        for record in self:
            record.code_qty = (
                record.python_code_qty + record.xml_code_qty + record.js_code_qty
            )

    def _recompute_module_type(self):
        rules = self.env["ir.module.type.rule"].search([])
        for module in self.search([("state", "=", "installed")]):
            module.module_type_id = rules._get_module_type_id_from_module(module)
