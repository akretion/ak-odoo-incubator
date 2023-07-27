# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

# TODO


class ProjectLoadReport(models.Model):
    _name = "project.load.report"
    _description = "Project Load Report"

    week = fields.Char()
    user_id = fields.Many2one("res.users", "User")
    total_planned_hours = fields.Float()
    project_planned_hours = fields.Float()
    project_capacity_hours = fields.Float()
    total_capacity_hours = fields.Float()
    reserved_capacity_hours = fields.Float()
    available_capacity_hours = fields.Float(
        help="min(total_capacity-reserved_capacity, project_capacity_hours)"
    )


#
#    """SELECT sum(hours)
#        FROM project_task_load_unit
#        GROUP BY week
#        WHERE project_id in %s"""
#
#    """SELECT sum(hours)
#        FROM project_user_capacity_unit
#        GROUP BY week
#        WHERE capacity_id in %s"""
#
#    # capacité réservé par autre
#    """SELECT sum(hours)
#        FROM project_user_capacity_unit
#        GROUP BY week
#        WHERE capacity_id not in %s"""
#
#    # capacité total
#    """SELECT sum(hours)
#        FROM project_user_capacity_unit
#        GROUP BY week
#    """
