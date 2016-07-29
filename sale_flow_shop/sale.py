# -*- encoding: utf-8 -*-
#########################################################################
#                                                                       #
#    Author: Chafique Delli                                             #
#    Copyright 2014 Akretion SA                                         #
#                                                                       #
#This program is free software: you can redistribute it and/or modify   #
#it under the terms of the GNU General Public License as published by   #
#the Free Software Foundation, either version 3 of the License, or      #
#(at your option) any later version.                                    #
#                                                                       #
#This program is distributed in the hope that it will be useful,        #
#but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#GNU General Public License for more details.                           #
#                                                                       #
#You should have received a copy of the GNU General Public License      #
#along with this program.  If not, see <http://www.gnu.org/licenses/>.  #
#########################################################################

from openerp.osv import fields, orm


class sale_shop(orm.Model):
    _inherit = "sale.shop"

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Address'),
    }


class sale_order(orm.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        invoice_vals = super(sale_order, self)._prepare_invoice(
            cr, uid, order, lines, context=context)
        invoice_vals['shop_id'] = order.shop_id.id
        return invoice_vals
