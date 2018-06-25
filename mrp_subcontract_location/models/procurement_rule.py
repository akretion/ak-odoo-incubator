# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#
##############################################################################
from odoo import models, fields, api, _


class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    @api.model
    def _get_action(self):
        return [('move_default_supplier_src', _('Move from default supplier location'))] + \
            super(ProcurementRule, self)._get_action()
