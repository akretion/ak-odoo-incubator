# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def mail_purchase_order_on_send(self):
        super(MailComposeMessage, self).mail_purchase_order_on_send()
        if not self.filtered('subtype_id.internal'):
            order = self.env['purchase.order'].browse(self._context['default_res_id'])
            if order.state == 'sent' and not self.env.context.get('send_rfq'):
                order.state = 'po_sent'
