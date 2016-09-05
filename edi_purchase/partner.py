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


class ResPartner(Model):
    _inherit = "res.partner"

    def _get_edi_purchase_profile_ids(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for id in ids:
            cr.execute("""
                SELECT DISTINCT purchase_edi_id
                FROM product_supplierinfo
                WHERE name = %s
            """, (id,))
            ids_sql = cr.fetchall()
            profile_ids = [profile[0] for profile in ids_sql if profile[0]]
            partner = self.browse(cr, uid, id, context=context)
            if partner.default_purchase_profile_id and \
                    partner.default_purchase_profile_id.id not in profile_ids:
                profile_ids.append(partner.default_purchase_profile_id.id)
            res[id] = profile_ids
            return res

    _columns = {
        'edi_purchase_profile_ids': fields.function(
            _get_edi_purchase_profile_ids,
            string='Edi Purchase Profiles',
            type='one2many',
            obj='purchase.edi.profile'),
        'default_purchase_profile_id': fields.many2one(
            'purchase.edi.profile',
            string="Default Purchase Profile",
            help="If no profile is configured on product, this default "
                 "profile will be used.")
    }

