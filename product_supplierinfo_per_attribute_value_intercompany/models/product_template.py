# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _get_intercompany_supplier_info_domain(self, pricelist):
        domain = super()._get_intercompany_supplier_info_domain(pricelist)
        domain.append(("product_attribute_value_ids", "=", False))
        return domain

    # TODO on V18 we need to improve this code to be able to call super
    def _has_intercompany_price(self, pricelist):
        self.ensure_one()
        return bool(
            self.env["product.pricelist.item"].search(
                [
                    ("pricelist_id", "=", pricelist.id),
                    ("product_tmpl_id", "=", self.id),
                    ("product_id", "=", False),
                    ("product_attribute_value_ids", "=", False),
                ]
            )
        )

    def _synchronise_supplier_info(self, pricelists=None):
        super()._synchronise_supplier_info(pricelists=pricelists)
        super(
            ProductTemplate, self.with_context(only_item_with_attribute=True)
        )._synchronise_supplier_info(pricelists=pricelists)
        if not pricelists:
            pricelists = self.env["product.pricelist"].search(
                [("is_intercompany_supplier", "=", True)]
            )

        def get_matching_supplier(suppliers, item):
            for supplier in suppliers:
                if (
                    supplier.product_attribute_value_ids
                    == item.product_attribute_value_ids
                ):
                    return supplier
            return self.env["product.supplierinfo"].with_context(
                automatic_intercompany_sync=True
            )

        for pricelist in pricelists:
            if not pricelist.is_intercompany_supplier:
                raise UserError(
                    _("The pricelist %s is not intercompany") % pricelist.name
                )
            for record in self.sudo().with_context(
                pricelist=pricelist.id, automatic_intercompany_sync=True
            ):
                # Note this do not work with price per quantity
                # We search all item with product_attribute_value_ids
                # and each of this item we ensure to have a corresponding
                # supplier
                # at the end we purge useless supplier
                items = self.env["product.pricelist.item"].search(
                    [
                        ("pricelist_id", "=", pricelist.id),
                        ("product_tmpl_id", "=", record.id),
                        ("product_id", "=", False),
                        ("product_attribute_value_ids", "!=", False),
                    ]
                )
                suppliers = record.seller_ids.filtered_domain(
                    [
                        ("intercompany_pricelist_id", "=", pricelist.id),
                        ("product_id", "=", False),
                        ("product_attribute_value_ids", "!=", False),
                    ]
                )
                new_suppliers = self.env["product.supplierinfo"]
                for item in items:
                    supplier = get_matching_supplier(suppliers, item)
                    vals = self._prepare_intercompany_supplier_info(pricelist)
                    self.uom_id._compute_price(item.fixed_price, self.uom_po_id)
                    vals["product_attribute_value_ids"] = [
                        (6, 0, item.product_attribute_value_ids.ids)
                    ]
                    if supplier:
                        supplier.write(vals)
                    else:
                        supplier.create(vals)
                    new_suppliers |= supplier

                to_delete = suppliers - new_suppliers
                to_delete.unlink()
