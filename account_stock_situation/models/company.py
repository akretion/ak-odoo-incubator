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
        value, attach = self._get_stock_valuation_another()
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

    def _get_stock_valuation_another(self):
        self.ensure_one()
        coef = self.cost_vs_purchase_threshold
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        if tools.config.get("running_env") == "dev":
            base_url = "http://anothercorp.localhost/"
        location_ids = [x.lot_stock_id.id for x in self.valued_warehouse_ids]
        # TODO conserver un group par emplacement : donc autant de colonnes
        # de nombres de produits que d'entrepots dans l'excel
        product_qties = self.env["stock.quant"].read_group(
            [("location_id", "child_of", location_ids)],
            ["product_id", "quantity"],
            ["product_id"],
        )
        product_ids = [x["product_id"][0] for x in product_qties]
        products = self.env["product.product"].browse(product_ids)
        prices = {
            x: x.variant_seller_ids and x.variant_seller_ids[0] or 0 for x in products
        }
        vals = defaultdict(list)
        for prd_q in product_qties:
            product = products.filtered(lambda s: s.id == prd_q["product_id"][0])
            vals["code"].append(product.default_code)
            vals["designation"].append(product.name)
            # TODO mettre une colonne qté par entrepot (x colonnes)
            vals["qté"].append(round(prd_q["quantity"]))
            # TODO quand la valeur est < cost_vs_purchase_threshold % de ce seuil
            # mettre une colonne 'check' à la valeur 1
            vals["valeur"].append(
                round(
                    max(
                        product.standard_price,
                        prices[product] and prices[product].price or 0 * coef / 100,
                    )
                    * prd_q["quantity"]
                )
            )
            # TODO mettre l'url en first column
            vals["lien"].append(
                f"{base_url}/web#id={prd_q['product_id'][0]}&cids={self.id}&action="
                f"{self.env.ref('product.product_normal_action_sell').id}&model="
                "product.product&view_type=form"
            )
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
        return sum(vals["valeur"]), attach
