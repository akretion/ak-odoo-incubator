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
            purchase, partner):
        purchase_line_obj = self.env['purchase.order.line']
        if not line_ids:
            return False
        purchase_lines = purchase_line_obj.browse(line_ids)
        datas = purchase_lines.get_edi_datas(edi_profile)
        attachment = purchase_line_obj.create_edi_file(
            datas, edi_profile, purchase)
        return attachment

    @api.multi
    def _send_edi_files(self, transfer_config, attachments):
        self.ensure_one()
        if transfer_config.edi_transfer_method == "external_location":
            for attachment in attachments:
                vals = self._get_edi_metadata_attachment_vals(transfer_config.edi_external_location_id, attachment)
                self.env["ir.attachment.metadata"].create(vals)
        elif transfer_config.edi_transfer_method == "mail":
            template_obj = self.env['mail.template']
            template = transfer_config.edi_mail_template_id
            if template.model_id.model == 'res.partner':
                record = self.partner_id
            elif template.model_id.model == 'purchase.order':
                record = self
            else:
                raise exceptions.UserError(
                    _("The mail template should be linked to partner or "
                      "purchase order."))
            values = template.generate_email(record.id)
            attachment_ids = attachments.ids
            if values['attachment_ids']:
                attachment_ids += values['attachment_ids']
            values['attachment_ids'] = [(6, 0, attachment_ids)]
            self.env['mail.mail'].create(values)

    @api.model
    def _get_edi_metadata_attachment_vals(self, location, attachment):
        tasks = [t for t in location.task_ids if t.method_type == 'export']
        task = tasks[0]
        return {
            'file_type': 'export_external_location',
            'task_id': task.id,
            'attachment_id': attachment.id,
        }

    @api.multi
    def send_edi_files(self, attachments_profile):
        self.ensure_one()
        attachment_by_transfer = {}
        # attachment could be send at different location depending on the profile
        # group all attachment per transfer method and then send it (the goal beeing
        # to send only one email if multiple file must be sent per mail)
        for attachment, profile in attachments_profile:
            transfer_config = profile.partner_edi_transport_config_ids.filtered(lambda x: x.partner_id == self.partner_id).edi_transport_config_id or self.partner_id.edi_transport_config_id
            if not transfer_config in attachment_by_transfer:
                attachment_by_transfer[transfer_config] = self.env["ir.attachment"]
            attachment_by_transfer[transfer_config] |= attachment
        for transfer_config, attachments in attachment_by_transfer.items():
            self._send_edi_files(transfer_config, attachments)

    @api.multi
    def generate_edi_files(self):
        self.ensure_one()
        partner = self.partner_id
        if not partner.edi_transport_config_id:
            return []
        # group lines per profile
        profile_lines_dict = {key: [] for key in self.partner_id.edi_purchase_profile_ids}
        for line in self.order_line:
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
        # generate 1 file per profile
        attachments_profile = []
        for edi_profile, line_ids in profile_lines_dict.items():
            attachment = self.generate_purchase_edi_file(
                edi_profile, line_ids, self, partner)
            if attachment:
                attachments_profile.append((attachment, edi_profile))
        return attachments_profile


    @api.multi
    def generate_and_send_edi_files(self):
        purchase_line_obj = self.env['purchase.order.line']
        for purchase in self:
            attachments_profile = purchase.generate_edi_files()
            purchase.send_edi_files(attachments_profile)
        return True

    @api.multi
    def button_approve(self):
        res = super(PurchaseOrder, self).button_approve()
        self.generate_and_send_edi_files()
        return res
