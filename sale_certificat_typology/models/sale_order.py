# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    certificat_item_ids = fields.One2many(
        comodel_name="sale.order.certificat.item",
        inverse_name="order_id",
        string="Certificat items",
    )
    sale_warn_msg = fields.Text(compute="_compute_sale_warn_msg")

    def action_confirm(self):
        for sale in self:
            if sale.certificat_item_ids.filtered(lambda ci: not ci.certificat_is_ok):
                raise ValidationError(
                    _(
                        "You cannot validate your order because some products "
                        "require certificates !"
                    )
                )
        return super().action_confirm()

    @api.depends("certificat_item_ids")
    def _compute_sale_warn_msg(self):
        for sale in self:
            sale_warn_msg = False
            if sale.state in ["draft", "sent"] and sale.certificat_item_ids.filtered(
                lambda ci: not ci.certificat_is_ok
            ):
                sale_warn_msg = _(
                    "Warning: in this order, some products require certificates !"
                )
            sale.sale_warn_msg = sale_warn_msg


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    certificat_item_ids = fields.Many2many(
        comodel_name="sale.order.certificat.item", string="Linked certificat items"
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line, vals in zip(lines, vals_list):
            if "order_id" in vals and "product_id" in vals:
                self._add_certificat_items(line, vals.get("product_id"))
        return lines

    def write(self, values):
        for line in self:
            if "product_id" in values:
                # remove certificat item for old product
                self._remove_certificat_items(line)
                # add certificat item for new product
                self._add_certificat_items(line, values.get("product_id"))
        return super().write(values)

    def unlink(self):
        for line in self:
            self._remove_certificat_items(line)
        return super().unlink()

    def _add_certificat_items(self, line, product_id):
        product = self.env["product.product"].browse(product_id)
        for certificat in product.required_certificat_ids:
            certificat_item = self.env["sale.order.certificat.item"].search(
                [
                    ("order_id", "=", line.order_id.id),
                    ("certificat_typology_id", "=", certificat.id),
                ],
                limit=1,
            )
            if certificat_item:
                certificat_item.write({"order_line_ids": [(4, line.id, 0)]})
            else:
                self.env["sale.order.certificat.item"].create(
                    {
                        "order_id": line.order_id.id,
                        "order_line_ids": [(6, 0, line.ids)],
                        "certificat_typology_id": certificat.id,
                        "company_id": line.company_id.id,
                    }
                )

    def _remove_certificat_items(self, line):
        certificat_items = self.env["sale.order.certificat.item"].search(
            [("order_id", "=", line.order_id.id), ("order_line_ids", "in", line.id)]
        )
        for item in certificat_items:
            if len(item.order_line_ids) == 1:
                item.unlink()
            else:
                item.write({"order_line_ids": [(3, line.id, 0)]})


class SaleOrderCertificatItem(models.Model):
    _name = "sale.order.certificat.item"
    _description = "Certificat Items in Sale Order"

    order_id = fields.Many2one(
        comodel_name="sale.order", string="Linked order", required=True
    )
    order_line_ids = fields.Many2many(
        comodel_name="sale.order.line", string="Linked order lines", required=True
    )
    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Concerned products",
        compute="_compute_product_ids",
        readonly=False,
    )
    certificat_typology_id = fields.Many2one(
        comodel_name="certificat.typology", string="Certificat typology", required=True
    )
    certificat = fields.Binary(string="Certificat", attachment=True)
    certificat_is_ok = fields.Boolean(string="Is valid ?")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")

    def _delete_documents_stored(self):
        certificat_items = self.search(
            [
                ("certificat", "!=", False),
                (
                    "certificat_typology_id.automatic_deletion",
                    "=",
                    "x_day_after_so_confirm",
                ),
                ("order_id.state", "not in", ["draft", "sent"]),
            ]
        )
        for item in certificat_items:
            if (
                date.today() - item.order_id.date_order.date()
            ).days >= item.certificat_typology_id.storage_duration:
                item.write({"certificat": False})

    @api.depends("order_line_ids")
    def _compute_product_ids(self):
        for rec in self:
            rec.product_ids = [(6, 0, rec.order_line_ids.mapped("product_id").ids)]
