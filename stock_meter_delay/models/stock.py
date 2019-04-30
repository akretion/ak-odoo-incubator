# coding: utf-8
# © 2015 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.depends("company_id", "company_id.warning_time", "max_date")
    def compute_start_warning_date(self):
        for rec in self:
            if rec.max_date:
                company = rec.company_id
                warning_time = company.warning_time
                max_date_dt = fields.Datetime.from_string(rec.max_date)
                start_warning_date = max_date_dt - relativedelta(
                    days=warning_time or 0.0
                )
                rec.start_warning_date = fields.Date.to_string(
                    start_warning_date
                )

    start_warning_date = fields.Date(
        string="Start Warning Date",
        compute="compute_start_warning_date",
        readonly=True,
        store=True,
    )


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    count_picking_late_soon = fields.Integer(compute="_get_picking_count_late")

    def _get_domains(self, vals):
        time_dt = fields.Datetime.context_timestamp(
            self, timestamp=datetime.datetime.now()
        )
        time_str = fields.Date.to_string(time_dt)
        vals = {
            "count_picking_late_soon": [
                ("start_warning_date", "<=", time_str),
                ("max_date", ">", time_str),
                (
                    "state",
                    "in",
                    (
                        "assigned",
                        "waiting",
                        "confirmed",
                        "partially_available",
                    ),
                ),
            ]
        }
        return vals

    def _get_picking_count_late(self):
        picking_obj = self.env["stock.picking"]
        domains = {}
        domains = self._get_domains(domains)
        for rec in self:
            for field in domains:
                data = picking_obj.read_group(
                    domains[field], ["picking_type_id"], ["picking_type_id"]
                )
                count = dict(
                    map(
                        lambda x: (
                            x["picking_type_id"] and x["picking_type_id"][0],
                            x["picking_type_id_count"],
                        ),
                        data,
                    )
                )
                rec.count_picking_late_soon = count.get(rec.id, 0)
