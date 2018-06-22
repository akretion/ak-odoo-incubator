# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, exceptions, _
import logging

_logger = logging.getLogger(__name__)


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.multi
    def _prepare_procurement_values(self, product_qty, date=False, group=False):
        vals = super(Orderpoint, self)._prepare_procurement_values(
            product_qty, date=date, group=group)
        # TODO put inter wh route as prefered route. We probably should add a
        # field on orderpoints to add this in option and not always.
        inter_wh_route = self.env.ref(
            'mrp_subcontract_location.route_interwarehouse_supply')
        vals['route_ids'] = [(6, 0, [inter_wh_route.id])]
        return vals
