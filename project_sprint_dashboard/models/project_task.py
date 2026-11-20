# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models

from .project_sprint import DASHBOARD_LEVEL


class ProjectTask(models.Model):
    _inherit = "project.task"

    sprint_id = fields.Many2one(tracking=True)
    sprint_history_ids = fields.Many2many(
        comodel_name="project.sprint",
        relation="project_task_sprint_history_rel",
        column1="task_id",
        column2="sprint_id",
        string="Sprint History",
        readonly=True,
        copy=False,
    )
    sprint_status = fields.Selection(
        selection=[
            ("todo", "To Start"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("canceled", "Canceled"),
        ],
        compute="_compute_sprint_status",
        store=True,
    )
    is_run = fields.Boolean(
        string="Run",
        compute="_compute_is_run",
        store=True,
    )

    def _get_sprint_status_depends(self):
        depends = ["state", "estimate_step_id"]
        if "effective_hours" in self._fields:
            depends.append("effective_hours")
        return depends

    @api.depends(lambda self: self._get_sprint_status_depends())
    def _compute_sprint_status(self):
        has_time = "effective_hours" in self._fields
        for task in self:
            if task.state == "1_done":
                task.sprint_status = "done"
            elif task.state == "1_canceled":
                task.sprint_status = "canceled"
            elif has_time and task.effective_hours:
                task.sprint_status = "in_progress"
            elif task.state == "04_waiting_normal" or not task.estimate_step_id:
                task.sprint_status = "todo"
            else:
                task.sprint_status = "in_progress"

    @api.depends("tag_ids", "project_id.run_tag_ids")
    def _compute_is_run(self):
        for task in self:
            task.is_run = bool(task.tag_ids & task.project_id.run_tag_ids)

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        tasks._update_sprint_history()
        tasks._assign_run_sprint()
        return tasks

    def write(self, vals):
        res = super().write(vals)
        if "sprint_id" in vals or "sprint_level_4_id" in vals:
            self._update_sprint_history()
        if {"state", "stage_id", "tag_ids"} & vals.keys():
            self._assign_run_sprint()
        return res

    def _update_sprint_history(self):
        tasks = self.filtered("sprint_level_4_id")
        for sprint, sprint_tasks in tasks.grouped("sprint_level_4_id").items():
            sprint_tasks.sprint_history_ids = [Command.link(sprint.id)]

    def _assign_run_sprint(self):
        tasks = self.filtered(
            lambda t: t.is_run
            and t.state == "1_done"
            and not t.sprint_id
            and t.project_id.use_sprint
        )
        for task in tasks:
            day = fields.Date.context_today(
                task, task.date_last_stage_update or fields.Datetime.now()
            )
            task.sprint_id = self.env["project.sprint"].search(
                [
                    ("level", "=", DASHBOARD_LEVEL),
                    ("date_start", "<=", day),
                    ("date_end", ">=", day),
                ],
                limit=1,
            )
