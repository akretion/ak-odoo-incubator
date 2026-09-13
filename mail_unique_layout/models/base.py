# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _get_mail_layout(self):
        return "mail_unique_layout.general_mail_layout"
