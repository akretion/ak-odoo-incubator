# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def _storage(self):
        self.ensure_one()
        if (
            self.name[-5:] == ".scss"
            or self.name[-3:] == ".js"
            or self.name[-4:] == ".css"
            or self.name in ("web_icon_data", "favicon")
        ):
            return "db"
        else:
            return super()._storage()
