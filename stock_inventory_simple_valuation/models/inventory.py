# © 2018 Mourad El Hadj Mimoun @ Akretion
# © 2018 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, fields, models

import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class StockInventory(models.Model):
    _inherit = ["stock.inventory", "mail.thread"]
    _name = "stock.inventory"

    def action_open_inventory_lines(self):
        action = super().action_open_inventory_lines()
        if self._context.get("valuation"):
            action["view_id"] = self.env.ref(
                "stock_inventory_simple_valuation.stock_inventory_line_tree_valuation"
            ).id
        return action


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    calc_product_cost = fields.Float(
        compute="_compute_product_cost",
        string="Computed cost",
        store=True,
        compute_sudo=True,
        digits=dp.get_precision("Account"),
    )
    manual_product_cost = fields.Float(
        string="Manual cost",
        digits=dp.get_precision("Account"),
    )
    total_value = fields.Float(
        compute="_compute_total_value",
        string="Value",
        store=True,
        compute_sudo=True,
        digits=dp.get_precision("Account"),
    )
    explanation = fields.Text(
        string="Source",
        compute="_compute_product_cost",
        store=True,
        compute_sudo=True,
        help="Explain computation method for each product",
    )
    origin_record_reference = fields.Char(
        string="Reference",
        compute="_compute_product_cost",
        store=True,
        compute_sudo=True,
    )
    origin_record_name = fields.Char(
        string="Document Name",
        compute="_compute_product_cost",
        store=True,
        compute_sudo=True,
    )

    @api.depends("calc_product_cost", "product_qty")
    def _compute_total_value(self):
        for line in self:
            line.total_value = line.calc_product_cost * line.product_qty

    @api.depends(
        "product_id",
        "product_qty",
        "manual_product_cost",
    )
    def _compute_product_cost(self):
        search_methods = self._get_search_methods()
        for record in self:
            if record.inventory_id and record.product_id:
                for method, method_name in search_methods:
                    res = getattr(record, method)()
                    if res:
                        record.explanation = method_name
                        record.calc_product_cost, origin = res
                        record.origin_record_name = origin.display_name
                        record.origin_record_reference = f"{origin._name},{origin.id}"
                        break
                else:
                    record.explanation = _("No Cost found")
                    record.calc_product_cost = 0.0
                    record.origin_record_reference = None
                    record.origin_record_name = None

    def _get_search_methods(self):
        """Overload this to customize price search methods
        they must: set calc_product_cost, explanation,
        origin_record_reference, origin_record_name,
        and return a bool indicating a result has been
        found"""
        return [
            ("_search_cost_manual", _("Manual setting")),
            ("_search_cost_invoice_lines", _("Invoice")),
            ("_search_cost_supplierinfo", _("Supplier info")),
            ("_search_cost_po_lines", _("Purchase Order")),
            ("_search_cost_standard_price", _("Standard price")),
        ]

    def _search_cost_manual(self):
        if self.manual_product_cost:
            return (self.manual_product_cost, None)

    def _search_cost_supplierinfo(self):
        sup_info = self.product_id._select_seller()
        if sup_info and sup_info[0].price:
            return (sup_info[0].price, sup_info[0])

    def _search_cost_invoice_lines(self):
        line = self.env["account.move.line"].search(
            [
                ("price_unit", "!=", 0),
                ("product_id", "=", self.product_id.id),
                ("move_id.state", "=", "posted"),
                ("move_id.move_type", "=", "in_invoice"),
                ("company_id", "=", self.env.company.id),
            ],
            order="create_date desc",
            limit=1,
        )
        if line:
            return (line.price_unit, line.move_id)

    def _search_cost_po_lines(self):
        po_line = self.env["purchase.order.line"].search(
            [
                ("price_unit", "!=", 0),
                ("product_id", "=", self.product_id.id),
                ("order_id.state", "in", ("purchase", "done")),
                ("company_id", "=", self.env.company.id),
            ],
            order="create_date desc",
            limit=1,
        )
        if po_line:
            return (po_line.price_unit, po_line.order_id)

    def _search_cost_standard_price(self):
        if self.product_id.standard_price:
            return (self.product_id.standard_price, self.product_id)
