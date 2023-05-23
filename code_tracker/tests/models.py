# Copyright 2023 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.code_tracker.decorators import tracker_code


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("state_id")
    def _onchange_state(self):
        super()._onchange_state()
        self.fonction_tracker_test()

    @tracker_code
    def fonction_tracker_test(self):
        return
