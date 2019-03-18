# -*- coding: utf-8 -*-

from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def open_purchase_request(self):
        action = self.env.ref(
            'procurement_purchase_request_button.purchase_request_action')
        action_dict = action.read()[0]
        action_dict['res_id'] = self.request_id.id
        action_dict['target'] = 'current'
        return action_dict
