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

from openerp.osv import fields, orm, osv
from tools.translate import _


class account_invoice(orm.Model):
    _inherit = "account.invoice"

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop'),
    }

    _defaults = {
        'shop_id': False
    }

    def onchange_shop_id(self, cr, uid, ids, type, shop_id, context=None):
        journal_id = False

        if shop_id:
            shop = self.pool.get('sale.shop').browse(
                cr, uid, shop_id, context=context)
            if type == 'out_invoice':
                if shop.journal_id.id:
                    journal_id = shop.journal_id.id
            elif type == 'out_refund':
                if shop.journal_id.refund_journal_id.id:
                    journal_id = shop.journal_id.refund_journal_id.id
                else:
                    raise osv.except_osv(
                        _('Warning'),
                        _('In the sale journal "%s", the refund journal is not specified !'
                          % shop.journal_id.name ))

        return {'value': {'journal_id': journal_id}}
