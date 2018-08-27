# coding: utf-8
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    purchase_id = fields.One2many(
        comodel_name='purchase.order', string='Related task',
        inverse_name='task_id',
    )
