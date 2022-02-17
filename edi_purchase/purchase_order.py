# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Akretion (<http://www.akretion.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, exceptions
from openerp.tools.translate import _

class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = ['purchase.order.line', 'edi.mixin']

class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order']

    @api.model
    def generate_purchase_edi_file(self, edi_profile, line_ids,
            purchase, partner, edi_transfer):
        purchase_line_obj = self.env['purchase.order.line']
        if not line_ids and not partner.edi_empty_file:
            return False
        purchase_lines = purchase_line_obj.browse(line_ids)
        datas = purchase_lines.get_edi_datas(edi_profile)
        attachment = purchase_line_obj.create_edi_file(
            datas, partner.edi_transfer_method, 
            edi_transfer, edi_profile, purchase)
        return attachment

    @api.model
    def send_edi_files(self, profile_lines_dict, purchase, partner,
                       edi_transfer):
        attachment_ids = []
        for edi_profile, line_ids in profile_lines_dict.iteritems():
            attachment = self.generate_purchase_edi_file(
                edi_profile, line_ids, purchase, partner,
                edi_transfer)
            if attachment:
                attachment_ids.append(attachment.id)
        # TODO FIXME we are forced to send mail from template on partner
        # Because in the case we want to send empty files, there are not
        # po.Maybe pass po_id in context if we rly need it in mail
        # template. Or find a better way ton send mail in both cases
        if partner.edi_transfer_method == 'mail' and attachment_ids:
            template_obj = self.env['mail.template']
            if edi_transfer.model_id.model == 'res.partner':
                record = purchase.partner_id
            elif edi_transfer.model_id.model == 'purchase.order':
                record = purchase
            else:
                raise exceptions.UserError(
                    _("The mail template should be linked to partner or "
                      "purchase order."))
            values = edi_transfer.generate_email(record.id)
            if values['attachment_ids']:
                attachment_ids += values['attachment_ids']
            values['attachment_ids'] = [(6, 0, attachment_ids)]
            self.env['mail.mail'].create(values)

    @api.multi
    def generate_and_send_edi_files(self):
        purchase_line_obj = self.env['purchase.order.line']
        for purchase in self:
            partner = purchase.partner_id
            edi_transfer = partner.edi_external_location_id or \
                           partner.edi_mail_template_id or \
                           partner.edi_transfer_method == 'manual' and 'manual' or \
                            False
            if not edi_transfer:
                continue
            profile_lines_dict = {key: [] for key in purchase.partner_id.edi_purchase_profile_ids}
            for line in purchase.order_line:
                product = line.product_id
                purchase_edi_id = False
                for seller in product.seller_ids:
                    if seller.name.id != partner.id:
                        continue
                    purchase_edi = seller.purchase_edi_id or False
                # Services should not appear in EDI file unless an EDI profile
                # is specifically on the supplier info. This way, we avoid
                # adding transport of potential discount or anything else
                # in the EDI file.
                if product.type == 'service' and not purchase_edi:
                    continue
                if purchase_edi:
                    profile_lines_dict[purchase_edi].append(line.id)
                elif partner.default_purchase_profile_id:
                    profile_lines_dict[partner.default_purchase_profile_id].\
                        append(line.id)
                else:
                    raise exceptions.UserError(
                        _("Some products don't have edi profile configured : %s") % (product.default_code,))
            self.send_edi_files(profile_lines_dict, purchase,
                purchase.partner_id, edi_transfer)

    @api.multi
    def button_approve(self):
        res = super(PurchaseOrder, self).button_approve()
        self.generate_and_send_edi_files()
        return res
