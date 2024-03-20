# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from io import StringIO
from os import linesep

from odoo import fields, models

from ..schema.invoice_footer import PIESegment
from ..schema.invoice_header import ENTSegment
from ..schema.invoice_line import LIGSegment
from ..schema.invoice_taxes import TVASegment
from ..schema.partner import PARSegment

_logger = logging.getLogger()


class AccountMove(models.Model):
    _inherit = ["account.move", "synchronize.exportable.mixin"]
    _name = "account.move"

    is_edi_exportable = fields.Boolean(
        related="partner_id.is_edi_exportable",
    )

    def _prepare_export_data(self, idx):
        self.ensure_one()
        res = []
        source_orders = self.line_ids.sale_line_ids.order_id
        # Segment Entete facture
        args = {
            "invoice": self,
            "source_orders": source_orders,
        }
        ent_segment = ENTSegment(**args).render()
        res.append(ent_segment)
        # segment partner
        args = {
            "invoice": self,
        }
        par_segment = PARSegment(**args).render()
        res.append(par_segment)
        # segment ligne de fatcure
        line_num = 0
        for line in self.invoice_line_ids:
            line_num += 1
            args = {
                "line": line,
                "line_num": line_num,
            }
            res.append(LIGSegment(**args).render())
        # Segment pied facture
        args = {
            "invoice": self,
        }
        pie_segment = PIESegment(**args).render()
        res.append(pie_segment)
        # segment ligne de TVA (détail des TVA)
        for tax_line in self.line_ids.filtered(lambda x: x.tax_line_id):
            args = {
                "tax_line": tax_line,
            }
            res.append(TVASegment(**args).render())
        # Segment END
        res.append("END")
        return res

    def _get_export_task(self):
        return self.env.ref("export_invoice_edi_auchan.export_to_auchan_ftp")

    def _prepare_aq_data(self, data):
        _logger.info(f"Exporting {self} to EDI Auchan")
        if self._name == "account.move":
            return self._format_to_exportfile_auchan_edi(data)
        return self._prepare_aq_data_csv(data)

    def _format_to_exportfile_auchan_edi(self, data):
        txt_file = StringIO()
        for row in data:
            txt_file.write(row)
            txt_file.write(linesep)
        txt_file.seek(0)

        return txt_file.getvalue().encode("utf-8")

    def _get_export_name(self):
        return self.name
