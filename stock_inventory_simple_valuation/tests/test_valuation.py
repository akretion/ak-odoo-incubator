# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests.common import TransactionCase


class TestStockInventoryValuation(TransactionCase):
    def setUp(self):
        super().setUp()
        ref = self.env.ref

        # default price guessing order:
        # supplierinfo
        # invoice
        # po
        # standard price
        # give up

        self.inventory = ref("stock.stock_inventory_0")
        self.large_cabinet_inventory_line = ref("stock.stock_inventory_line_3")
        self.large_cabinet_inventory_line_qty = 500
        self.large_cabinet = ref("product.product_product_6")
        self.large_cabinet_po = ref("purchase.purchase_order_4")
        self.large_cabinet_po_line = ref(
            "purchase.purchase_order_4"
        ).order_line.filtered(lambda r: r.product_id.id == self.large_cabinet.id)
        self.large_cabinet_invoice = ref(
            "l10n_generic_coa.demo_invoice_equipment_purchase"
        )

    def _clearUp(self, toClear):
        # discard existing demo data
        if "supplierinfo" in toClear:
            self.large_cabinet.seller_ids.unlink()
        if "standard price" in toClear:
            self.large_cabinet.standard_price = 0.0
            self.large_cabinet.list_price = 0.0
        if "po" in toClear:
            self.large_cabinet_po.button_cancel()
            self.large_cabinet_po.unlink()
        if "invoice" in toClear:
            self.large_cabinet_invoice.state = "draft"

    def test_manual_cost(self):
        new_manual_cost = 1.11
        self.large_cabinet_inventory_line.manual_product_cost = new_manual_cost
        self.inventory.line_ids._refresh_product_cost()
        self.assertEqual(
            new_manual_cost,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_force_valuation_cost(self):
        force_valuation = 1.33
        self.large_cabinet_inventory_line.product_id.force_valuation = force_valuation
        self.inventory.line_ids._refresh_product_cost()
        self.assertEqual(
            force_valuation,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_search_supplierinfo(self):
        new_supplierinfo_price = 3.33
        for supplierinfo in self.large_cabinet.seller_ids:
            supplierinfo.price = new_supplierinfo_price
        self.inventory.line_ids._refresh_product_cost()
        self.assertEqual(
            new_supplierinfo_price,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_search_invoice_lines(self):
        self._clearUp(["supplierinfo"])

        invoice_vals = {
            "partner_id": self.env.ref("base.res_partner_12").id,
            "move_type": "in_invoice",
            "invoice_date": fields.Date.context_today(self.env.user),
            "invoice_line_ids": [
                (
                    0,
                    None,
                    {
                        "price_unit": 5.62,
                        "name": "whatever",
                        "quantity": 123.4,
                        "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                        "display_type": False,
                        "product_id": self.large_cabinet.id,
                    },
                )
            ],
        }

        invoice_with_cabinet = self.env["account.move"].create(invoice_vals)
        invoice_with_cabinet.action_post()
        self.inventory.line_ids._refresh_product_cost()
        self.assertEqual(
            invoice_with_cabinet.invoice_line_ids[0].price_unit,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_search_po_lines(self):
        self._clearUp(["supplierinfo", "invoice"])
        self.large_cabinet_po_line.price_unit = 2.222
        self.large_cabinet_po.button_confirm()
        # purchase/models/purchase.py l 324: confirming a PO
        # generates a supplierinfo if there are less than 10
        self._clearUp(["supplierinfo"])
        self.inventory.line_ids._refresh_product_cost()
        self.assertEqual(
            self.large_cabinet_po_line.price_unit,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_search_standard_price(self):
        self._clearUp(["supplierinfo", "po", "invoice"])
        self.large_cabinet.standard_price = 8.88
        self.inventory.line_ids._refresh_product_cost()
        self.assertEqual(
            self.large_cabinet.standard_price,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_give_up(self):
        self._clearUp(["supplierinfo", "po", "standard price", "invoice"])
        self.inventory.line_ids._refresh_product_cost()
        self.assertEqual(0.0, self.large_cabinet_inventory_line.calc_product_cost)
        self.assertFalse(self.large_cabinet_inventory_line.origin_record_reference)
