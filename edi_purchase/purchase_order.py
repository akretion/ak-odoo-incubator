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

from openerp.osv.orm import Model
from openerp.osv import fields, orm
from openerp.tools.translate import _

class PurchaseOrderLine(Model):
    _name = 'purchase.order.line'
    _inherit = ['purchase.order.line', 'edi.mixin']

class PurchaseOrder(Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order']

    def generate_purchase_edi_file(self, cr, uid, edi_profile, line_ids,
            purchase, partner, edi_transfer, context=None):
        purchase_line_obj = self.pool['purchase.order.line']
        if not line_ids and not partner.edi_empty_file:
            return False
        fields, fields_name = purchase_line_obj.get_fields_from_export(
            cr, uid, edi_profile.export_id.id, context=context)
        datas = purchase_line_obj.get_edi_datas(
            cr, uid, line_ids, fields, fields_name,
            edi_profile.file_format, context=context)
        attachment_id = purchase_line_obj.create_edi_file(
            cr, uid, datas, partner.edi_transfer_method, 
            edi_transfer, edi_profile, purchase)
        return attachment_id

    def send_edi_files(self, cr, uid, profile_lines_dict, purchase, partner,
                       edi_transfer, context=None):
        attachment_ids = []
        for edi_profile, line_ids in profile_lines_dict.iteritems():
            attachment_id = self.generate_purchase_edi_file(
                cr, uid, edi_profile, line_ids, purchase, partner,
                edi_transfer, context=context)
            if attachment_id:
                attachment_ids.append(attachment_id)

        # TODO FIXME we are forced to send mail from template on partner
        # Because in the case we want to send empty files, there are not
        # po.Maybe pass po_id in context if we rly need it in mail
        # template. Or find a better way ton send mail in both cases
        if partner.edi_transfer_method == 'mail' and attachment_ids:
            template_obj = self.pool['email.template']
            values = template_obj.generate_email(
                cr, uid, edi_transfer.id, purchase.partner_id.id,
                context=context)
            if values['attachment_ids']:
                attachment_ids += values['attachment_ids']
            values['attachment_ids'] = [(6, 0, attachment_ids)]
            mail_id = self.pool['mail.mail'].create(
                cr, uid, values, context=context)

    def generate_and_send_edi_files(self, cr, uid, ids, context=None):
        purchase_line_obj = self.pool['purchase.order.line']
        for purchase in self.browse(cr, uid, ids, context=context):
            partner = purchase.partner_id
            edi_transfer = partner.edi_repository_id or \
                           partner.edi_mail_template_id or \
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
                    purchase_edi_id = seller.purchase_edi_id or False
                if purchase_edi_id:
                    profile_lines_dict[purchase_edi_id].append(line.id)
                else:
                    raise orm.except_orm(
                        _('Warning!'),
                        _("Some products don't have edi profile configured : %s") % (product.default_code,))
            self.send_edi_files(cr, uid, profile_lines_dict, purchase,
                purchase.partner_id, edi_transfer, context=context)
        return

    def wkf_approve_order(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(PurchaseOrder, self).wkf_approve_order(
            cr, uid, ids, context=context)
        self.generate_and_send_edi_files(cr, uid, ids, context=context)
        return res

