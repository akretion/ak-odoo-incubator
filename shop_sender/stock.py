# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) All Rights Reserved 2014 Akretion
#    @author David BEAL <david.beal@akretion.com>
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
###############################################################################

from openerp.osv import orm


class StockPickingOut(orm.Model):
    _inherit = 'stock.picking.out'

    def _customize_sender_address(self, cr, uid, picking, context=None):
        partner = super(StockPickingOut, self)._customize_sender_address(
            cr, uid, picking, context=context)
        if 'shop_id' in self._columns:
            if picking.shop_id.partner_id:
                return picking.shop_id.partner_id
        return partner
