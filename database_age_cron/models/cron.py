# -*- coding: utf-8 -*-
# Copyright 2021 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrCronDoNoting(models.BaseModel):
    _inherit = "ir.cron"

    @api.model
    def do_nothing(self):
        pass
