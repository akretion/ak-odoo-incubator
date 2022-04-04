# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

HOURS_PER_DAYS = 8. # TODO Make it configurable


class ProjectTask(models.Model):
    _inherit = 'project.task'

    allowed_estimate_step_ids = fields.Many2many(
        comodel_name='project.estimate.step',
        related="project_id.estimate_step_ids",
        string='Allowed Estimate Step')
    estimate_step_id = fields.Many2one(
        "project.estimate.step",
        "Estimate Step",
        index=True,
        group_expand="_read_group_estimate_step_id")

    # TODO move in an other module project_time_in_days ?
    planned_days = fields.Float(
        "Planned Days",
        compute="_compute_planned_days",
        store=True)
    remaining_days = fields.Float(
        "Remaining Days",
        compute="_compute_remaining_days",
        store=True)
    effective_days = fields.Float(
        "Effective Days",
        compute="_compute_effective_days",
        store=True)

    @api.model
    def _read_group_estimate_step_id(self, steps, domain, order):
        if 'default_project_id' in self._context:
            project = self.env["project.project"].browse(self._context["default_project_id"])
            steps |= project.estimate_step_ids
        return steps.sorted("days")

    def _convert_to_days(self, value):
        uom_day = self.env.ref("uom.product_uom_day")
        uom_hour = self.env.ref("uom.product_uom_hour")
        return uom_hour._compute_quantity(value, uom_day)

    def _convert_to_hours(self, value):
        uom_day = self.env.ref("uom.product_uom_day")
        uom_hour = self.env.ref("uom.product_uom_hour")
        return uom_day._compute_quantity(value, uom_hour)

    @api.depends("planned_hours")
    def _compute_planned_days(self):
        for record in self:
            record.planned_days = self._convert_to_days(record.planned_hours)

    @api.depends("remaining_hours")
    def _compute_remaining_days(self):
        for record in self:
            record.remaining_days = self._convert_to_days(record.remaining_hours)

    @api.depends("effective_hours")
    def _compute_effective_days(self):
        for record in self:
            record.effective_days = self._convert_to_days(record.effective_hours)

    def _sync_estimate(self):
        for record in self:
            record.planned_hours = self._convert_to_hours(record.estimate_step_id.days)

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
