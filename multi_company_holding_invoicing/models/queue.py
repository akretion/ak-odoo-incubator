# -*- coding: utf-8 -*-
from odoo import fields, models


class QueueJob(models.Model):
    _inherit = 'queue.job'

    holding_invoice_id = fields.Many2one(
        comodel_name='account.invoice', string=u'Holding Invoice',
        copy=False, readonly=True)
