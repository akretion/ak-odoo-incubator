# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _store_in_db(self, mimetype):
        return (
            mimetype in ("text/scss", "text/css", "application/javascript")
            or self._context.get("force_db_storage")
            or (len(self) == 1 and self.name in ("web_icon_data", "favicon"))
        )

    def _get_datas_related_values(self, data, mimetype):
        if self._store_in_db(mimetype):
            return {
                "file_size": len(data),
                "checksum": self._compute_checksum(data),
                "index_content": self._index(data, mimetype),
                "store_fname": False,
                "db_datas": data,
            }
        else:
            return super()._get_datas_related_values(data, mimetype)

    @api.model_create_multi
    def create(self, vals_list):
        records = self.browse(False)
        for vals in vals_list:
            if vals.get("name") in ("web_icon_data", "favicon"):
                self = self.with_context(force_db_storage=True)
            records |= super(IrAttachment, self).create([vals])
        return records
