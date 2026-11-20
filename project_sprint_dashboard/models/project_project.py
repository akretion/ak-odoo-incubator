# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    run_tag_ids = fields.Many2many(
        comodel_name="project.tags",
        relation="project_project_run_tag_rel",
        column1="project_id",
        column2="tag_id",
        string="Run Tags",
        help="Tasks with one of these tags are run work (debug, urgent, out of "
        "sprint planning). A done run task without sprint is put in the sprint "
        "of its closing date.",
    )

    def action_open_sprint_dashboard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "project_sprint_dashboard.action_sprint_dashboard"
        )
        action["params"] = {"partner_id": self.partner_id.commercial_partner_id.id}
        return action
