# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .project_sprint import MAX_SPRINT_DEPTH


class ProjectTask(models.Model):
    _inherit = "project.task"

    use_sprint = fields.Boolean(related="project_id.use_sprint")

    sprint_id = fields.Many2one("project.sprint")
    sprint_level_1_id = fields.Many2one(
        "project.sprint",
        string="Sprint Top Level",
        compute="_compute_sprint_levels",
        domain="[('level', '=', 1)]",
        store=True,
        readonly=False,
    )
    sprint_level_2_id = fields.Many2one(
        "project.sprint",
        string="Sprint Second Level",
        compute="_compute_sprint_levels",
        domain="[('level', '=', 2), ('parent_id', '=', sprint_level_1_id)]",
        store=True,
        readonly=False,
    )
    sprint_level_3_id = fields.Many2one(
        "project.sprint",
        string="Sprint Third Level",
        compute="_compute_sprint_levels",
        domain="[('level', '=', 3), ('parent_id', '=', sprint_level_2_id)]",
        store=True,
        readonly=False,
    )
    sprint_level_4_id = fields.Many2one(
        "project.sprint",
        string="Sprint Fourth Level",
        compute="_compute_sprint_levels",
        domain="[('level', '=', 4), ('parent_id', '=', sprint_level_3_id)]",
        store=True,
        readonly=False,
    )

    planned_date_start = fields.Datetime(
        compute="_compute_planned_date_start_end_from_sprint",
        store=True,
        readonly=False,
    )
    planned_date_end = fields.Datetime(
        compute="_compute_planned_date_start_end_from_sprint",
        store=True,
        readonly=False,
    )

    @api.depends("sprint_id")
    def _compute_sprint_levels(self):
        for task in self.with_context(sprint_compute=True):
            sprint = task.sprint_id
            sprint_level = sprint.level if sprint else 1

            current_sprint = sprint
            for level in range(sprint_level, 0, -1):
                setattr(task, f"sprint_level_{level}_id", current_sprint)
                current_sprint = current_sprint.parent_id if current_sprint else False

            for level in range(sprint_level + 1, MAX_SPRINT_DEPTH + 1):
                setattr(task, f"sprint_level_{level}_id", False)

    # The following methods are used to update the sprint_id field when the user
    # changes the sprint_level_X_id fields.
    # I couldn't do it with only computes, if someone has a better idea, I'm all ears.
    @api.onchange("sprint_level_1_id")
    def _onchange_sprint_level_1(self):
        self.sprint_id = self.sprint_level_1_id

    @api.onchange("sprint_level_2_id")
    def _onchange_sprint_level_2(self):
        self.sprint_id = self.sprint_level_2_id

    @api.onchange("sprint_level_3_id")
    def _onchange_sprint_level_3(self):
        self.sprint_id = self.sprint_level_3_id

    @api.onchange("sprint_level_4_id")
    def _onchange_sprint_level_4(self):
        self.sprint_id = self.sprint_level_4_id

    @api.depends("sprint_id.date_start", "sprint_id.date_end")
    def _compute_planned_date_start_end_from_sprint(self):
        for record in self:
            if record.sprint_id:
                record.planned_date_end = record.sprint_id.date_end
                record.planned_date_start = record.sprint_id.date_start

    def read(self, fields, load="_classic_read"):
        return super(
            ProjectTask,
            self.with_context(short_name=True),
        ).read(fields, load)
