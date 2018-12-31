# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################
from openerp import models, api, fields, exceptions, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    open_order = fields.Boolean(
        help="This picking come from an Open Order and can't be transfered")

    @api.multi
    def do_transfer(self):
        for picking in self:
            if picking.open_order:
                raise exceptions.Warning(
                    _('The picking comes from an Open Order. It is not '
                      'possible to transfer it.'))
        return super(StockPicking, self).do_transfer()
