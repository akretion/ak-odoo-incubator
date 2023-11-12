# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models

# number of line per a page of a book
QTY_PER_PAGE = 35


class IrModuleType(models.Model):
    _inherit = "ir.module.type"

    sequence = fields.Integer()
    code_qty = fields.Integer(
        string="Code Quantity", compute="_compute_code_qty", store=True
    )
    page_qty = fields.Integer(
        string="Page Qty", compute="_compute_code_qty", store=True
    )
    source = fields.Selection(
        [
            ("standard", "Standard"),
            ("community", "Community"),
            ("custom", "Custom"),
        ]
    )
    migration_price_unit = fields.Float()
    maintenance_price_unit = fields.Float()
    migration_monthly_price = fields.Float(compute="_compute_migration_price")
    migration_year_price = fields.Float(compute="_compute_migration_price")
    maintenance_monthly_price = fields.Float(compute="_compute_maintenance_price")
    maintenance_year_price = fields.Float(compute="_compute_maintenance_price")

    @api.depends("migration_price_unit")
    def _compute_migration_price(self):
        return self._compute_total_price("migration")

    @api.depends("maintenance_price_unit")
    def _compute_maintenance_price(self):
        return self._compute_total_price("maintenance")

    def _compute_total_price(self, case):
        for record in self:
            record[f"{case}_monthly_price"] = record[f"{case}_price_unit"] * round(
                record.code_qty / 100
            )
            record[f"{case}_year_price"] = record[f"{case}_monthly_price"] * 12

    @api.depends("module_ids.code_qty")
    def _compute_code_qty(self):
        for record in self:
            record.code_qty = sum(
                record.module_ids.filtered(lambda l: l.state == "installed").mapped(
                    "code_qty"
                )
            )
            record.page_qty = record.code_qty / QTY_PER_PAGE
