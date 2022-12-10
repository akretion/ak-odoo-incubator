# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _register_hook(self):
        super()._register_hook()
        self.env.cr.execute(
            """
            SELECT id
            FROM ir_attachment
            WHERE db_datas IS NULL
            AND (
                name='web_icon_data'
                OR name='favicon'
                OR name ilike '%.js'
                OR name ilike '%.css'
                OR name ilike '%.scss'
            )"""
        )
        ids = [x[0] for x in self.env.cr.fetchall()]
        if len(ids) > 0:
            _logger.info("Migrate %s asset Attachment into database", len(ids))
        for attachment in self.browse(ids):
            attachment.write(
                {"datas": attachment.datas, "mimetype": attachment.mimetype}
            )

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
