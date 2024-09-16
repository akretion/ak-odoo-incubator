# Copyright 2023 Akretion (https://www.akretion.com).
# @author Chafique Delli <chafique.delli@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def read(self, fields=None, load="_classic_read"):
        res = super().read(fields=fields, load=load)
        if self.env.context.get("pos_id") and fields:
            if "taxes_id" in fields:
                pos_config = self.env["pos.config"].browse(self._context.get("pos_id"))
                fp = pos_config.force_fiscal_position_id
                if fp:
                    map_tax = defaultdict(list)
                    for item in fp.tax_ids:
                        map_tax[item.tax_src_id.id].append(item.tax_dest_id.id)
                    for res_line in res:
                        res_line["taxes_id"] = [
                            mapped_tax
                            for tax_id in res_line["taxes_id"]
                            for mapped_tax in map_tax.get(tax_id, [tax_id])
                        ]
        return res
