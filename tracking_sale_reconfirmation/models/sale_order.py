# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


def _get_tracked_fnames(env, model_name):
    custom_per_model = env["ir.model"]._get_custom_tracked_fields_per_model()
    if model_name in custom_per_model:
        return set(custom_per_model[model_name])
    tracked = set()
    for fname, field in env[model_name]._fields.items():
        if getattr(field, "tracking", None):
            tracked.add(fname)
    return tracked


def _field_label(env, model_name, fname):
    field = env[model_name]._fields.get(fname)
    if field:
        return field.get_description(env).get("string", fname)
    return fname


def _field_display(record, fname):
    field = record._fields.get(fname)
    if field is None:
        return ""
    val = record[fname]
    if field.type == "many2one":
        return val.display_name or ""
    if field.type in ("many2many", "one2many"):
        return ", ".join(val.mapped("display_name"))
    if field.type == "boolean":
        return str(val)
    return val if val is not False and val is not None else ""


def _blacklisted_fnames(env, model_name):
    return ["order_line"] if model_name == "sale.order" else []


def _capture_snapshot(record, model_name):
    fnames = _get_tracked_fnames(record.env, model_name)
    snapshot = {}
    for fname in fnames:
        if fname in record._fields and fname not in _blacklisted_fnames(
            record.env, model_name
        ):
            snapshot[fname] = _field_display(record, fname)
    return snapshot


def _diff_and_record(env, record, model_name, before, tracking, source):
    fnames = _get_tracked_fnames(env, model_name)
    for fname in fnames:
        if fname not in record._fields:
            continue
        old = before.get(fname, "")
        new = _field_display(record, fname)
        if str(old) != str(new):
            tracking._add_change(
                source=source,
                field_label=_field_label(env, model_name, fname),
                old_value=old,
                new_value=new,
            )


class SaleOrder(models.Model):
    _inherit = "sale.order"
    active_cancel_tracking_id = fields.Many2one(
        comodel_name="sale.cancel.tracking",
        string="Active Cancel Tracking",
        copy=False,
        index=True,
    )
    cancel_tracking_ids = fields.One2many(
        comodel_name="sale.cancel.tracking",
        inverse_name="sale_order_id",
        string="Cancel Tracking History",
    )
    cancel_tracking_count = fields.Integer(
        string="# Cancel Cycles",
        compute="_compute_cancel_tracking_count",
    )

    @api.depends("cancel_tracking_ids")
    def _compute_cancel_tracking_count(self):
        for rec in self:
            rec.cancel_tracking_count = len(rec.cancel_tracking_ids)

    def action_cancel(self):
        res = super().action_cancel()
        for order in self.filtered(lambda o: o.state == "cancel"):
            tracking = self.env["sale.cancel.tracking"].create(
                {
                    "sale_order_id": order.id,
                    "cancel_date": fields.Datetime.now(),
                    "state": "cancelled",
                }
            )
            order.active_cancel_tracking_id = tracking
        return res

    def action_draft(self):
        orders_with_tracking = self.filtered(
            lambda o: o.state == "cancel" and o.active_cancel_tracking_id
        )
        res = super().action_draft()
        for order in orders_with_tracking:
            order.active_cancel_tracking_id.write(
                {
                    "state": "draft",
                    "draft_date": fields.Datetime.now(),
                }
            )
        return res

    def action_confirm(self):
        orders_with_tracking = self.filtered(lambda o: o.active_cancel_tracking_id)
        res = super().action_confirm()
        for order in orders_with_tracking:
            order.active_cancel_tracking_id.write(
                {
                    "state": "done",
                    "confirm_date": fields.Datetime.now(),
                }
            )
            order.active_cancel_tracking_id = False
        return res

    def write(self, vals):
        snapshots_before = {}
        for order in self:
            if order.active_cancel_tracking_id and order.state == "draft":
                snapshots_before[order.id] = _capture_snapshot(order, "sale.order")

        res = super().write(vals)

        for order in self:
            if not order.active_cancel_tracking_id or order.state != "draft":
                continue
            before = snapshots_before.get(order.id)
            if not before:
                continue
            _diff_and_record(
                self.env,
                order,
                "sale.order",
                before,
                order.active_cancel_tracking_id,
                "order",
            )
        return res

    def action_view_cancel_trackings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Cancel / Reconfirm History",
            "res_model": "sale.cancel.tracking",
            "view_mode": "list,form",
            "domain": [("sale_order_id", "=", self.id)],
            "context": {"default_sale_order_id": self.id},
        }


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, vals):
        snapshots_before = {}
        for line in self:
            order = line.order_id
        res = super().write(vals)
        for line in self:
            order = line.order_id
            if not order.active_cancel_tracking_id or order.state != "draft":
                continue
            before = snapshots_before.get(line.id)
            if not before:
                continue
            _diff_and_record(
                self.env,
                line,
                "sale.order.line",
                before,
                order.active_cancel_tracking_id,
                f"line: {line.product_id.display_name or '?'}",
            )
        return res

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            order = line.order_id
            if order.active_cancel_tracking_id and order.state == "draft":
                order.active_cancel_tracking_id._add_change(
                    source=f"line: {line.product_id.display_name or '?'}",
                    field_label="Line added",
                    old_value="",
                    new_value=line.display_name or line.name or "",
                )
        return lines

    def unlink(self):
        to_track = []
        for line in self:
            order = line.order_id
            if order.active_cancel_tracking_id and order.state == "draft":
                to_track.append(
                    (
                        order.active_cancel_tracking_id,
                        f"line: {line.product_id.display_name or '?'}",
                        line.display_name or line.name or "",
                    )
                )
        res = super().unlink()
        for tracking, source, label in to_track:
            tracking._add_change(
                source=source,
                field_label="Line removed",
                old_value=label,
                new_value="",
            )
        return res
