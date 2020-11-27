# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _storage(self):
        self.ensure_one()
        if self.name.startswith("/web/content/") or self.name == "web_icon_data":
            return "db"
        else:
            return super()._storage()
