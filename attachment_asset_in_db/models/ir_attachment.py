# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _is_an_asset(self, vals):
        return vals.get("name") in ("web_icon_data", "favicon") or vals.get(
            "mimetype"
        ) in ("text/scss", "text/css", "application/javascript")

    def _process_db_asset(self, vals):
        self._check_contents(vals)
        if self._is_an_asset(vals):
            vals["db_datas"] = vals.pop("datas")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._process_db_asset(vals)
        return super().create(vals_list)

    def write(self, vals):
        if "datas" in vals:
            self._process_db_asset(vals)
        return super().write(vals)
