# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    code_qty = fields.Integer(
        string="total code quantity (python, xml, js)",
        compute="_compute_code_qty",
        store=False,
    )
    currency_id = fields.Many2one(
        "res.currency", "Currency", compute="_compute_currency_id"
    )
    monthly_price = fields.Monetary(
        string="Prix mensuel (maintenance + migration)",
        compute="_compute_monthly_price",
        store=False,
    )
    monthly_price_increase_if_installed = fields.Monetary(
        string="Prix additionnel si installé",
        compute="_compute_monthly_price_increase_if_installed",
        store=False,
    )

    def _compute_currency_id(self):
        for record in self:
            record.currency_id = self.env.company.currency_id

    @api.depends("installed_version")
    def _compute_code_qty(self):
        for record in self:
            record.code_qty = (
                record.python_code_qty + record.xml_code_qty + record.js_code_qty
            )

    def _recompute_module_type(self):
        rules = self.env["ir.module.type.rule"].search([])
        for module in self.search([("state", "=", "installed")]):
            module.module_type_id = rules._get_module_type_id_from_module(module)

    @api.depends("state", "code_qty")
    def _compute_monthly_price(self):
        for record in self:
            maintenance_price = (
                record.code_qty * record.module_type_id.maintenance_price_unit / 100
            )
            migration_price = (
                record.code_qty * record.module_type_id.migration_price_unit / 100
            )
            record.monthly_price = maintenance_price + migration_price

    @api.depends("state", "code_qty")
    def _compute_monthly_price_increase_if_installed(self):
        for record in self:
            if record.state == "installed":
                record.monthly_price_increase_if_installed = 0
            else:
                record.monthly_price_increase_if_installed = record.monthly_price
                if record.dependencies_id and record.dependencies_id.filtered(
                    lambda l: l.state != "installed"
                ):
                    children_names = record.mapped("dependencies_id.name")
                    uninstalled_children = self.search(
                        [
                            ("name", "in", children_names),
                            ("state", "in", ["uninstalled", "uninstallable"]),
                        ]
                    )
                    record.monthly_price_increase_if_installed += sum(
                        uninstalled_children.mapped(
                            "monthly_price_increase_if_installed"
                        )
                    )
