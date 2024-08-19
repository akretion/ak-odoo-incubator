import base64
import io
from collections import defaultdict

import polars as pl

from odoo import fields, models, tools
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    valued_warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse",
        domain=lambda self: [("company_id", "=", self.env.company.id)],
    )
    stock_journal_id = fields.Many2one(comodel_name="account.journal")
    cost_vs_purchase_threshold = fields.Integer(string="Seuil en %")
    account_purchase_stock_id = fields.Many2one(comodel_name="account.account")
    account_stock_id = fields.Many2one(comodel_name="account.account")

    def _set_account_stock_valuation(self, company_string_id):
        self = self.env.ref(company_string_id)
        value, attach = self._get_stock_valuation()
        for mfield in (
            "account_stock_id",
            "account_purchase_stock_id",
            "stock_journal_id",
        ):
            if not self[mfield]:
                raise UserError(
                    f"Le champ '{mfield}' n'est pas défini: vérifiez les "
                    "paramètres intitulés 'Valorisation de stock'"
                )
        move = self.env["account.move"].create(
            {
                "journal_id": self.stock_journal_id.id,
                "company_id": self.id,
                "to_check": True,
                "move_type": "entry",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.account_stock_id.id,
                            "name": "stock",
                            "debit": 0,
                            "credit": value,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.account_purchase_stock_id.id,
                            "name": "stock",
                            "debit": value,
                            "credit": 0,
                        },
                    ),
                ],
            }
        )
        attach.res_id = move.id

    def _get_stock_valuation(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        if tools.config.get("running_env") == "dev":
            base_url = "http://anothercorp.localhost/"
        location_ids = [x.lot_stock_id.id for x in self.valued_warehouse_ids]
        stock_quant_ids = self.env["stock.quant"].search(
            [("location_id", "child_of", location_ids)],
        )
        products = self.env["product.product"].browse(stock_quant_ids.product_id.ids)
        vals = defaultdict(list)
        product_dict = {}
        for stock_quant in stock_quant_ids:
            if stock_quant.product_id.id not in product_dict:
                product_dict[stock_quant.product_id.id] = [
                    stock_quant.warehouse_id,
                    stock_quant.quantity,
                ]
            else:
                if (
                    stock_quant.warehouse_id
                    in product_dict.get(stock_quant.product_id.id)[0]
                ):
                    product_dict[stock_quant.product_id.id][1] += stock_quant.quantity
                else:
                    product_dict[stock_quant.product_id.id] += [
                        stock_quant.warehouse_id,
                        stock_quant.quantity,
                    ]
        for product_id, warehouse_quantities in product_dict.items():
            product = products.filtered(lambda s: s.id == product_id)
            vals["link"].append(
                f"{base_url}/web#id={product_id}&cids={self.id}&action="
                f"{self.env.ref('product.product_normal_action_sell').id}&model="
                "product.product&view_type=form"
            )
            vals["code"].append(product.default_code)
            vals["designation"].append(product.name)
            for i in range(0, len(warehouse_quantities), 2):
                warehouse_id = warehouse_quantities[i]
                quantity = warehouse_quantities[i + 1]
                vals[f"qty_{warehouse_id.code}"].append(round(quantity))
            if len(warehouse_quantities) / 2 < len(self.valued_warehouse_ids):
                warehouse_without_qty = self.valued_warehouse_ids.filtered(
                    lambda r: r.id
                    not in [
                        warehouse_quantities[i].id
                        for i in range(0, len(warehouse_quantities), 2)
                    ]
                )
                for warehouse in warehouse_without_qty:
                    vals[f"qty_{warehouse.code}"].append(0)

            vals["value"].append(round(product.standard_price))
        df = pl.from_dict(vals)
        mfile = io.BytesIO()
        df.write_excel(workbook=mfile)
        attach = self.env["ir.attachment"].create(
            {
                "name": "Valorisation_stock_jourdain",
                "type": "binary",
                "res_model": "account.move",
                "datas": base64.b64encode(mfile.getvalue()),
            }
        )
        return sum(vals["value"]), attach
