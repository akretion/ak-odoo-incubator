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
        compute="_compute_certificat_item_ids",
        string="Certificat items",
        store=True,
    )
    sale_warn_msg = fields.Text(compute="_compute_sale_warn_msg")

    @api.depends("order_line.product_id")
    def _compute_certificat_item_ids(self):
        for record in self:
            required_certificats = record.order_line.product_id.required_certificat_ids
            items = record.certificat_item_ids.filtered(
                lambda s: s.certificat_typology_id in required_certificats
            )
            for certificat in required_certificats:
                if certificat not in items.certificat_typology_id:
                    items |= self.env["sale.order.certificat.item"].create(
                        {
                            "order_id": record.id,
                            "certificat_typology_id": certificat.id,
                            "company_id": record.company_id.id,
                        }
                    )
            record.certificat_item_ids = [(6, 0, items.ids)]

    @api.depends("certificat_item_ids")
    def _compute_sale_warn_msg(self):
        for sale in self:
            sale_warn_msg = False
            if sale.state in ["draft", "sent"] and sale.certificat_item_ids.filtered(
                lambda ci: not ci.certificat_is_ok
            ):
                sale_warn_msg = _(
                    "Warning: in this order, some products require valid certificates !"
                )
            sale.sale_warn_msg = sale_warn_msg

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


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    required_certificat_ids = fields.Many2many(
        comodel_name="certificat.typology",
        related="product_id.required_certificat_ids",
        string="Requested certificats",
        readonly=True,
    )


class SaleOrderCertificatItem(models.Model):
    _name = "sale.order.certificat.item"
    _description = "Certificat Items in Sale Order"

    order_id = fields.Many2one(comodel_name="sale.order", string="Linked order")
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
