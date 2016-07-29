# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    Model module for OpenERP                                                   #
#    Copyright (C) 2011 Akretion                                                #
#    author : Sébastien BEAU <sebastien.beau@akretion.com>                      #
#             Chafique DELLI <chafique.delli@akretion.com>                      #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from osv import orm
import netsvc


class StockPicking(orm.Model):
    _inherit = "stock.picking"

    def __init__(self, pool, cr):
        super(StockPicking, self).__init__(pool, cr)
        option = ('started', 'Started')
        state_selection = self._columns['state'].selection
        if option not in state_selection:
            pos = state_selection.index(('done', 'Transferred'))
            state_selection.insert(pos, option)


class StockPickingOut(orm.Model):
    _inherit = "stock.picking.out"

    def __init__(self, pool, cr):
        super(StockPickingOut, self).__init__(pool, cr)
        option = ('started', 'Started')
        state_selection = self._columns['state'].selection
        if option not in state_selection:
            pos = state_selection.index(('done', 'Delivered'))
            state_selection.insert(pos, option)

    def unstart(self, cr, uid, ids, context=None):
        for picking_id in ids:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(
                uid, 'stock.picking', picking_id, 'button_unstart', cr)
        return True

    def start(self, cr, uid, ids, context=None):
        for picking_id in ids:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_validate(
                uid, 'stock.picking', picking_id, 'button_start', cr)
        return True
