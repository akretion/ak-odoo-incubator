# -*- coding: utf-8 -*-
# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    def delay_to_wh(self, dest):
        """Delay between current warehouse and dest.

        It's the time in days, between the Picking Out
        and the Picking In
        """
        return self.env['inter_wh.delay'].search([
            ('source_wh_id', '=', self.id),
            ('dest_wh_id', '=', dest.id),
        ]).delay or 0
