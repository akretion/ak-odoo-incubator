# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import ast

from odoo import fields, models
from odoo.osv import expression


class ProjectLoadCapacityReport(models.TransientModel):
    _name = "project.load.capacity.report"
    _description = "Project Load Capacity Report"

    project_ids = fields.Many2many(comodel_name="project.project", string="Project")
    line_ids = fields.One2many(
        "project.load.capacity.report.line", "report_id", "Lines"
    )

    def _generate_lines(self):
        capacities = self.env["project.user.capacity"].search([])
        match_capacities = self.env["project.user.capacity"]
        if self.project_ids:
            projects = self.project_ids
            for project in self.project_ids:
                for capacity in capacities:
                    if project.filtered_domain(capacity.filter_id.domain):
                        match_capacities |= capacities
        else:
            match_capacities = capacities
            projects = self.env["project.project"].search([])

        # TODO fix domain (it's a string, it's expect a list)
        domain = []
        for capacity in match_capacities:
            if capacity.filter_id.domain:
                capacity_domain = ast.literal_eval(capacity.filter_id.domain)
            else:
                capacity_domain = []
            domain = expression.OR([domain, capacity_domain])
        match_projects = self.env["project.project"].search(domain)

        # TODO add timesheet to know what have been done this week
        self.env.cr.execute(
            """
            INSERT INTO project_load_capacity_report_line (
                report_id,
                total_capacity_hours,
                total_planned_hours,
                project_capacity_hours,
                project_planned_hours,
                project_available_hours,
                week,
                user_id
                )
                SELECT
                    %s AS report_id,
                    total_capacity.hours as total_capacity_hours,
                    total_planned.hours as total_planned_hours,
                    project_capacity.hours as project_capacity_hours,
                    project_planned.hours as project_planned_hours,
                    project_capacity_hours -
                    match_project_planned_hours as project_available_hours,
                    total_capacity.week as week,
                    total_capacity.user_id
                FROM (
                    SELECT week, user_id, sum(hours) as hours
                        FROM project_capacity_unit
                        GROUP BY week, user_id
                    ) AS total_capacity
                FULL JOIN (
                    SELECT week, user_id, sum(hours) as hours
                        FROM project_workload_unit
                        GROUP BY week, user_id
                    ) AS total_planned
                    ON total_capacity.week = total_planned.week
                    AND total_capacity.user_id = total_planned.user_id
                FULL JOIN (
                    SELECT week, user_id, sum(hours) as hours
                        FROM project_capacity_unit
                        WHERE capacity_id in %s
                        GROUP BY week, user_id
                    ) AS project_capacity
                    ON total_capacity.week = project_capacity.week
                    AND total_capacity.user_id = project_capacity.user_id
                FULL JOIN (
                    SELECT week, user_id, sum(hours) as hours
                        FROM project_workload_unit
                        WHERE project_id in %s
                        GROUP BY week, user_id
                    ) AS match_project_planned
                    ON total_capacity.week = match_project_planned.week
                    AND total_capacity.user_id = match_project_planned.user_id
                FULL JOIN (
                    SELECT week, user_id, sum(hours) as hours
                        FROM project_workload_unit
                        WHERE project_id in %s
                        GROUP BY week, user_id
                    ) AS project_planned
                    ON total_capacity.week = project_planned.week
                    AND total_capacity.user_id = project_planned.user_id
        """,
            (
                self.id,
                tuple(match_capacities.ids),
                tuple(match_projects.ids),
                tuple(projects.ids),
            ),
        )
        self.env.clear()

    def refresh_lines(self):
        self.line_ids.unlink()
        # self._generate_lines()
        return True

    def open_report(self):
        self.refresh_lines()
        action = (
            self.env.ref("project_workload.project_load_capacity_report_line_action")
            .sudo()
            .read()[0]
        )
        action["domain"] = [("report_id", "=", self.id)]
        return action


class ProjectLoadReportLine(models.TransientModel):
    _name = "project.load.capacity.report.line"
    _description = "Project Load Report Line"

    week = fields.Char()
    user_id = fields.Many2one("res.users", "User")
    total_planned_hours = fields.Float()
    total_capacity_hours = fields.Float()
    project_planned_hours = fields.Float()
    project_capacity_hours = fields.Float()
    project_available_hours = fields.Float()
    report_id = fields.Many2one("project.load.capacity.report", "Report")
