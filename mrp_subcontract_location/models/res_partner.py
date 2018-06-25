# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # TODO constraint so both location are not equal (if set)
    reception_location_id = fields.Many2one(
        'stock.location', string="Supplier Reception Location",
        help="The location should belong to the supplier warehouse.")
    manufacture_location_id = fields.Many2one(
        'stock.location', string="Supplier Manufacture Location",
        help="The location should belong to the supplier warehouse.")
