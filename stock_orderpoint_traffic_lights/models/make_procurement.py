# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo import api, fields, models


class MakeProcurement(models.TransientModel):
    _inherit = 'make.procurement'

    dlt = fields.Float(
        'Decoupled Lead Time', related='product_id.dlt')

    @api.onchange('product_id')
    def _calc_date_planned(self):
        '''Use minimal viable date.

        Dlt + today is the sooner date we can propose.
        It's not a default func because product_id not set
        on load.
        '''
        today = datetime.today()
        delta = relativedelta(days=int(self.product_id.dlt))
        res = fields.Date.to_string(
            today + delta
        )
        self.date_planned = res
