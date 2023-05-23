# Copyright 2023 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TrackerCodeInfo(models.Model):
    _name = "tracker.code.info"
    _description = "see if a function is used"

    function_name = fields.Char(string="Function name")
    model_name = fields.Char(string="Model name")
    running_time = fields.Datetime(string="Running time")
    user = fields.Char(string="User")
    log_trace = fields.Text(string="Logger")
