# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

HOURS_PER_DAYS = 8.0  # TODO Make it configurable


class ProjectTask(models.Model):
    _inherit = "project.task"

    allowed_estimate_step_ids = fields.Many2many(
        comodel_name="project.estimate.step",
        related="project_id.estimate_step_ids",
        string="Allowed Estimate Step",
    )
    estimate_step_id = fields.Many2one(
        "project.estimate.step",
        "Estimate Step",
        index=True,
        group_expand="_read_group_estimate_step_id",
    )

    @api.model
    def _read_group_estimate_step_id(self, steps, domain, order):
        if "default_project_id" in self._context:
            project = self.env["project.project"].browse(
                self._context["default_project_id"]
            )
            steps |= project.estimate_step_ids
        return steps.sorted("days")

    def _sync_estimate(self):
        for record in self:
            record.planned_hours = record.project_id.convert_days_to_hours(
                record.estimate_step_id.days
            )

    def write(self, vals):
        super().write(vals)
        if "estimate_step_id" in vals:
            self._sync_estimate()
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if any(["estimate_step_id" in vals for vals in vals_list]):
            records._sync_estimate()
        return records

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        if self._context.get("no_empty_stage"):
            return stages
        else:
            return super()._read_group_stage_ids(stages, domain, order)
