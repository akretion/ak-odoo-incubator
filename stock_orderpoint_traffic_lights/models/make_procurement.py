# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import datetime
from odoo import api, fields, models


class MakeProcurement(models.TransientModel):
    _inherit = 'make.procurement'

    dlt = fields.Float(
        'Decoupled Lead Time', related='product_id.dlt')
