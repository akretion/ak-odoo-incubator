# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleCancelTracking(models.Model):
    _name = "sale.cancel.tracking"
    _description = "Sale Cancel/Reconfirm Tracking"

    name = fields.Char(
        compute="_compute_name",
        string="Description",
        store=True,
    )

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
    )
    partner_id = fields.Many2one(
        related="sale_order_id.partner_id",
        string="Customer",
    )
    company_id = fields.Many2one(
        related="sale_order_id.company_id",
    )
    user_id = fields.Many2one(
        related="sale_order_id.user_id",
        string="Salesperson",
    )

    cancel_date = fields.Datetime(
        string="Cancelled On",
        readonly=True,
    )
    draft_date = fields.Datetime(
        string="Reset to Draft On",
        readonly=True,
    )
    confirm_date = fields.Datetime(
        string="Reconfirmed On",
        readonly=True,
    )

    state = fields.Selection(
        selection=[
            ("cancelled", "Cancelled"),
            ("draft", "In Draft"),
            ("done", "Reconfirmed"),
        ],
        string="Cycle State",
        default="cancelled",
        readonly=True,
    )

    change_line_ids = fields.One2many(
        comodel_name="sale.cancel.tracking.line",
        inverse_name="tracking_id",
        string="Changes",
    )
    change_count = fields.Integer(
        string="Changes Count",
        compute="_compute_change_count",
    )

    @api.depends("change_line_ids")
    def _compute_change_count(self):
        for rec in self:
            rec.change_count = len(rec.change_line_ids)

    def _add_change(self, source, field_label, old_value, new_value):
        self.ensure_one()
        self.env["sale.cancel.tracking.line"].create(
            {
                "tracking_id": self.id,
                "source": source,
                "field_label": field_label,
                "old_value": str(old_value) if old_value is not None else "",
                "new_value": str(new_value) if new_value is not None else "",
                "change_date": fields.Datetime.now(),
                "sale_order_id": self.sale_order_id.id,
            }
        )

    @api.depends("sale_order_id")
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.sale_order_id.name}-{len(rec.sale_order_id.cancel_tracking_ids) or 1}"


class SaleCancelTrackingLine(models.Model):
    _name = "sale.cancel.tracking.line"
    _description = "Sale Cancel Tracking Change Line"

    tracking_id = fields.Many2one(
        comodel_name="sale.cancel.tracking",
    )
    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
    )

    change_date = fields.Datetime(
        string="Changed On",
    )
    source = fields.Char()
    field_label = fields.Char(
        string="Field",
    )
    old_value = fields.Char(
        string="Before",
    )
    new_value = fields.Char(
        string="After",
    )
