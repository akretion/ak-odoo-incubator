# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################
from openerp import models, fields, api, exceptions, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    origin_order_id = fields.Many2one('purchase.order',
        string="Origin Purchase Order")
