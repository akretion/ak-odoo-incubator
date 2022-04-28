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

from openerp import models, fields


class PartnerProfileEdi(models.Model):
    _name = "partner.profile.edi"
    _description = "Transport Edi Config per partner/profile"

    partner_id = fields.Many2one("res.partner", string="Supplier", required=True, domain="[('edi_transport_config_id', '!='', False)]")
    edi_transport_config_id = fields.Many2one("edi.transport.config", required=True, string="EDI Transport Configuration")
    edi_profile_id = fields.Many2one("purchase.edi.profile", required=True)


class PurchaseEdiProfile(models.Model):
    _name = "purchase.edi.profile"
    _inherit = "edi.profile"

    suppplier_info_ids = fields.One2many(
        'product.supplierinfo',
        'purchase_edi_id',
        'Suppliers Info')
    export_id = fields.Many2one(domain=[('resource', '=', 'purchase.order.line')])
    partner_edi_transport_config_ids = fields.One2many("partner.profile.edi", "edi_profile_id",
        string="Partner Transport Configuration",
        help="Choose a method to send EDI files if different from the one on the supplier")


