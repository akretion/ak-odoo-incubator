# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict
from datetime import datetime, timedelta

from odoo import api, fields, models

from odoo.addons.project_workload.models.project_task_workload import week_name


class ProjectUserCapacity(models.Model):
    _name = "project.user.capacity"
    _description = "Project User Capacity"

    name = fields.Char(required=True)
    user_id = fields.Many2one("res.users", "User", required=True)
    filter_id = fields.Many2one("ir.filters", "Domain")
    line_ids = fields.One2many("project.user.capacity.line", "capacity_id", "Line")
    unit_ids = fields.One2many("project.capacity.unit", "capacity_id", "Capacity Unit")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._generate_capacity_unit()
        return records

    def _cron_generate_week_report(self, nbr_week=52):
        self.search([])._generate_capacity_unit(nbr_week=nbr_week)

    def _generate_capacity_unit(self, nbr_week=52):
        now = datetime.now()
        items = self.env["project.capacity.unit"].search(
            [("week", ">=", week_name(now))]
        )
        weeks_per_capacity = defaultdict(set)
        for item in items:
            weeks_per_capacity[item.capacity_id.id].add(item.week)
        weeks = {week_name(now + timedelta(days=7 * x)) for x in range(nbr_week)}
        vals_list = []
        for capacity in self:
            missing_weeks = weeks - weeks_per_capacity[capacity.id]
            vals_list += [
                {
                    "week": week,
                    "capacity_id": capacity.id,
                }
                for week in missing_weeks
            ]
        return self.env["project.capacity.unit"].create(vals_list)
