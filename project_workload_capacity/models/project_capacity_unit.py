# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from datetime import datetime

from odoo import api, fields, models

from odoo.addons.project_workload.models.project_task_workload import (
    WEEK_FORMAT,
    week_name,
)


class ProjectCapacityUnit(models.Model):
    _name = "project.capacity.unit"
    _description = "Project Capacity Unit"
    _rec_name = "week"
    _order = "week asc"

    week = fields.Char()
    capacity_id = fields.Many2one("project.user.capacity", "Capacity")
    hours = fields.Float(compute="_compute_capacity", store=True)
    user_id = fields.Many2one(
        "res.users", "User", related="capacity_id.user_id", store=True
    )
    _sql_constraints = [
        (
            "week_capacity_uniq",
            "unique(week, capacity_id)",
            "The week must be uniq per capacity",
        ),
    ]

    @api.depends(
        "capacity_id.line_ids.hours",
        "capacity_id.line_ids.date_start",
        "capacity_id.line_ids.date_end",
        "capacity_id.line_ids.modulo",
    )
    def _compute_capacity(self):
        for record in self:
            hours = 0
            for line in record.capacity_id.line_ids:
                start = week_name(line.date_start)
                stop = week_name(line.date_end)
                if record.week >= start and (not stop or record.week <= stop):
                    if line.modulo > 1:
                        nbr_week = round(
                            (
                                datetime.strptime(
                                    record.week + "-1", WEEK_FORMAT + "-%w"
                                ).date()
                                - datetime.strptime(
                                    start + "-1", WEEK_FORMAT + "-%w"
                                ).date()
                            ).days
                            / 7
                        )
                        if nbr_week % line.modulo:
                            # week is not a multi skip it
                            continue
                    hours = line.hours
                    break
            record.hours = hours
