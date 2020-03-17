# © 2018 Mourad El Hadj Mimoun @ Akretion
# © 2018 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, models, fields, _
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class StockInventory(models.Model):
    _inherit = ["stock.inventory", "mail.thread"]
    _name = "stock.inventory"

    def button_compute_line_costs(self):
        self.ensure_one()
        self.line_ids._compute_product_cost()


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    calc_product_cost = fields.Float(
        compute="_compute_product_cost",
        string="Computed cost",
        store=True,
        digits_compute=dp.get_precision("Account"),
    )
    manual_product_cost = fields.Float(
        string="Manual cost", digits_compute=dp.get_precision("Account")
    )
    total_value = fields.Float(
        compute="_compute_total_value",
        string="Value",
        store=True,
        digits_compute=dp.get_precision("Account"),
    )
    explanation = fields.Text(
        string="Source",
        compute="_compute_product_cost",
        store=True,
        help="Explain computation method for each product",
    )
    origin_record_reference = fields.Char(
        string="Reference", compute="_compute_product_cost", store=True
    )
    origin_record_name = fields.Char(
        string="Document Name", compute="_compute_product_cost", store=True
    )

    @api.onchange("manual_product_cost")
    def _onchange_manual_product_cost(self):
        self._compute_product_cost()

    @api.depends("calc_product_cost", "manual_product_cost", "product_qty")
    def _compute_total_value(self):
        for line in self:
            if line.manual_product_cost:
                line.total_value = line.manual_product_cost * line.product_qty
            else:
                line.total_value = line.calc_product_cost * line.product_qty

    @api.depends(
        "product_id", "product_qty", "manual_product_cost",
    )
    def _compute_product_cost(self):
        # sudo because it is unlikely the user has access rights to all
        # relevant models
        self = self.sudo()
        lines = self.filtered(lambda r: r.inventory_id and r.product_id)
        lines_manual = lines.filtered(lambda r: r.manual_product_cost)
        lines_manual._compute_product_cost_manual()
        lines_calc = lines - lines_manual
        search_methods = self._get_search_methods()
        for record in lines_calc:
            for method in search_methods:
                if getattr(record, method)():
                    break

    def _compute_product_cost_manual(self):
        for rec in self:
            rec.calc_product_cost = rec.manual_product_cost
            rec.explanation = _("Manual setting")
            rec.origin_record_reference = _("n/a")
            rec.origin_record_name = _("n/a")

    def _get_search_methods(self):
        """Overload this to customize price search methods
        they must: set calc_product_cost, explanation,
        origin_record_reference, origin_record_name,
        and return a bool indicating a result has been
        found"""
        res = [
            "_search_cost_supplierinfo",
            "_search_cost_invoice_lines",
            "_search_cost_po_lines",
            "_search_cost_standard_price",
            "_search_cost_give_up",
        ]
        return res

    def get_search_method_strings(self):
        """Overload this to customize what appears on
        the excel report"""
        res = [
            _("les informations fournisseur de la fiche produit"),
            _("les dernières factures d'achat"),
            _("les dernières commandes d'achats"),
            _("le coût manuel de la fiche produit"),
        ]
        return res

    def _search_cost_supplierinfo(self):
        sup_info = self.product_id.seller_ids
        if sup_info and sup_info[0].price:
            self.calc_product_cost = sup_info[0].price
            self.explanation = _("Supplier info")
            self.origin_record_reference = (
                "product.supplierinfo,%s" % sup_info[0].id
            )
            self.origin_record_name = sup_info[0].name.name
            return True
        return False

    def _search_cost_invoice_lines(self):
        most_recent_invoice_line = self.env["account.invoice.line"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("invoice_id.state", "in", ("open", "paid")),
                ("invoice_id.type", "=", "in_invoice"),
            ],
            order="create_date desc",
            limit=1,
        )
        if most_recent_invoice_line:
            self.calc_product_cost = most_recent_invoice_line.price_unit
            self.explanation = _("Invoice")
            self.origin_record_reference = (
                "account.invoice,%s" % most_recent_invoice_line.invoice_id.id
            )
            self.origin_record_name = most_recent_invoice_line.invoice_id.name
            return True
        return False

    def _search_cost_po_lines(self):
        po_line = self.env["purchase.order.line"].search(
            [
                ("product_id", "=", self.product_id.id),
                ("order_id.state", "in", ("purchase", "done")),
            ],
            limit=1,
        )
        if po_line:
            self.calc_product_cost = po_line.price_unit
            self.explanation = _("Purchase Order")
            self.origin_record_reference = (
                "purchase.order,%s" % po_line.order_id.id
            )
            self.origin_record_name = po_line.order_id.name
            return True
        return False

    def _search_cost_standard_price(self):
        if self.product_id.standard_price:
            self.calc_product_cost = self.product_id.standard_price
            self.explanation = _("Standard price")
            self.origin_record_reference = (
                "product.product,%s" % self.product_id.id
            )
            self.origin_record_name = self.product_id.name
            return True
        return False

    def _search_cost_give_up(self):
        self.explanation = _("No Cost found")
        self.calc_product_cost = 0.0
        self.origin_record_reference = "n/a"
        self.origin_record_name = _("None")
        return True
