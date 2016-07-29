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


class stock_picking(orm.Model):
    _inherit = "stock.picking"

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop'),
    }

    _defaults = {
        'shop_id': False
    }


class stock_picking_out(orm.Model):
    _inherit = "stock.picking.out"

    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop'),
    }

    _defaults = {
        'shop_id': False
    }