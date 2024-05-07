# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from io import StringIO
from os import linesep

from odoo import fields, models

from ..schema.base import SegmentInterfaceExc
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

    def _find_bl_info(self):
        """Find entête "Numéro de BL" and date"""
        raise NotImplementedError

    def _render_segment(self, segment, vals):
        try:
            res = segment(**vals).render()
        except SegmentInterfaceExc as e:
            self.env.context["export_auchan_errors"].append(str(e))
        else:
            return res

    def _prepare_export_data(self, idx):
        self.ensure_one()
        _logger.info(f"Exporting {self.name}")
        res = []
        source_orders = self.line_ids.sale_line_ids.order_id
        bl_nbr, bl_date = self._find_bl_info()
        self = self.with_context(export_auchan_errors=[])
        # Segment Entete facture
        res.append(
            self._render_segment(
                ENTSegment,
                {
                    "invoice": self,
                    "source_orders": source_orders,
                    "bl_nbr": bl_nbr,
                    "bl_date": bl_date,
                },
            )
        )
        # segment partner
        res.append(
            self._render_segment(
                PARSegment,
                {
                    "invoice": self,
                },
            )
        )
        # segment ligne de fatcure
        for idx, line in enumerate(self.invoice_line_ids, start=1):
            res.append(
                self._render_segment(
                    LIGSegment,
                    {
                        "line": line,
                        "line_num": str(idx),
                    },
                )
            )
        # Segment pied facture
        res.append(
            self._render_segment(
                PIESegment,
                {
                    "invoice": self,
                },
            )
        )
        # segment ligne de TVA (détail des TVA)
        for tax_line in self.line_ids.filtered(lambda x: x.tax_line_id):
            res.append(
                self._render_segment(
                    TVASegment,
                    {
                        "tax_line": tax_line,
                    },
                )
            )
        # Segment END
        res.append("END")
        errs = self.env.context.get("export_auchan_errors")
        if errs:
            errstr = "Erreur lors de la génération du fichier Auchan: \n"
            errstr += "\n".join(errs)
            _logger.error(errstr)
            raise ValueError(errstr)
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
        return self.name.replace("/", "-")
