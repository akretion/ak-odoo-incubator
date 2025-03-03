# Copyright 2025 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    main_supplier_partner_id = fields.Many2one(
        "res.partner", "Supplier", compute="_compute_supplier_info"
    )
    main_supplier_margin = fields.Float(compute="_compute_supplier_info")
    main_supplier_price = fields.Float(compute="_compute_supplier_info")
    main_supplier_info = fields.Text(compute="_compute_supplier_info")

    def _prepare_info_name(self, seller):
        tmpl_values = seller.product_id.product_template_attribute_value_ids
        values = (
            tmpl_values.product_attribute_value_id or seller.product_attribute_value_ids
        )
        if values:
            return ", ".join(values.mapped("name"))
        else:
            return "_"

    @api.depends(
        "product_tmpl_id.seller_ids.price",
        "product_tmpl_id.seller_ids.name",
        "product_tmpl_id.seller_ids.min_qty",
        "product_tmpl_id.seller_ids.date_start",
        "product_tmpl_id.seller_ids.date_end",
        "product_tmpl_id.seller_ids.sequence",
        "product_tmpl_id.seller_ids.product_id",
        "product_tmpl_id.seller_ids.product_attribute_value_ids",  # in a glue module ?
    )
    def _compute_supplier_info(self):
        # Following code is not optimal when having a lot of variante
        # But it's simple code ;)
        for record in self:
            sellers = self.env["product.supplierinfo"]
            if record.product_id:
                sellers = record.product_id._select_seller(quantity=record.min_quantity)
            elif record.product_tmpl_id:
                for variant in record.product_tmpl_id.product_variant_ids:
                    if record._is_applicable_for(variant, record.min_quantity):
                        sellers |= variant._select_seller(quantity=record.min_quantity)
            if not sellers:
                record.update(
                    {
                        "main_supplier_partner_id": None,
                        "main_supplier_margin": 0,
                        "main_supplier_price": 0,
                        "main_supplier_info": "",
                    }
                )
            else:
                sellers = sellers.sorted("price", reverse=True)
                seller = sellers[0]
                if len(sellers) > 1 and seller.price > sellers[-1].price:
                    info = "- " + "\n- ".join(
                        [
                            (
                                format(seller.price, "g")
                                + f" : {self._prepare_info_name(seller)}"
                            )
                            for seller in sellers
                        ]
                    )
                else:
                    info = ""
                if seller.price:
                    margin = (record.fixed_price - seller.price) / record.fixed_price
                else:
                    margin = 0
                record.update(
                    {
                        "main_supplier_partner_id": seller.name.id,
                        "main_supplier_margin": margin,
                        "main_supplier_price": seller.price,
                        "main_supplier_info": info,
                    }
                )
