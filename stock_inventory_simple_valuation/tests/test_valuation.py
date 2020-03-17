# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
        ).order_line.filtered(
            lambda r: r.product_id.id == self.large_cabinet.id
        )
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
        self.inventory.button_compute_line_costs()
        self.assertEqual(
            new_manual_cost,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_search_supplierinfo(self):
        new_supplierinfo_price = 3.33
        for supplierinfo in self.large_cabinet.seller_ids:
            supplierinfo.price = new_supplierinfo_price
        self.inventory.button_compute_line_costs()
        self.assertEqual(
            new_supplierinfo_price,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_search_invoice_lines(self):
        self._clearUp(["supplierinfo"])
        invoice_vals = {
            "partner_id": self.env.ref("base.res_partner_12").id,
            "type": "in_invoice",
        }
        invoice_with_cabinet = self.env["account.invoice"].create(invoice_vals)
        new_invoice_price = 5.555
        invoice_line_vals = {
            "invoice_id": invoice_with_cabinet.id,
            "price_unit": new_invoice_price,
            "name": "whatever",
            "quantity": 123.4,
            "product_uom": self.env.ref("uom.product_uom_unit"),
            "display_type": False,
            "account_id": invoice_with_cabinet.account_id.id,
            "product_id": self.large_cabinet.id,
        }
        invoice_line_with_cabinet = self.env["account.invoice.line"].create(
            invoice_line_vals
        )
        invoice_with_cabinet.action_invoice_open()
        self.inventory.button_compute_line_costs()
        self.assertEqual(
            invoice_line_with_cabinet.price_unit,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_search_po_lines(self):
        self._clearUp(["supplierinfo", "invoice"])
        self.large_cabinet_po_line.price_unit = 2.222
        self.large_cabinet_po.button_confirm()
        # purchase/models/purchase.py l 324: confirming a PO
        # generates a supplierinfo if there are less than 10
        self._clearUp(["supplierinfo"])
        self.inventory.button_compute_line_costs()
        self.assertEqual(
            self.large_cabinet_po_line.price_unit,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_search_standard_price(self):
        self._clearUp(["supplierinfo", "po", "invoice"])
        self.large_cabinet.standard_price = 8.88
        self.inventory.button_compute_line_costs()
        self.assertEqual(
            self.large_cabinet.standard_price,
            self.large_cabinet_inventory_line.calc_product_cost,
        )

    def test_give_up(self):
        self._clearUp(["supplierinfo", "po", "standard price", "invoice"])
        self.inventory.button_compute_line_costs()
        self.assertEqual(
            0.0, self.large_cabinet_inventory_line.calc_product_cost
        )
        self.assertEqual(
            "n/a", self.large_cabinet_inventory_line.origin_record_reference
        )
