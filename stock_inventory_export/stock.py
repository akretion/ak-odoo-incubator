# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 AKRETION
#    @author Chafique Delli <chafique.delli@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import models, api


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    @api.multi
    def write(self, vals):
        if 'line_ids' in vals and 'install_mode' in self._context:
            for inventory in self:
                for import_line in vals.get('line_ids'):
                    product_uom_id = import_line[2]['product_uom_id']
                    location_id = import_line[2]['location_id']
                    product_id = import_line[2]['product_id']
                    prod_lot_id = import_line[2]['prod_lot_id']
                    product_qty = import_line[2]['product_qty']
                    for inventory_line in inventory.line_ids:
                        if inventory_line.product_uom_id.id\
                                == product_uom_id and\
                                inventory_line.location_id.id\
                                == location_id and\
                                inventory_line.product_id.id\
                                == product_id and\
                                inventory_line.prod_lot_id.id\
                                == prod_lot_id and\
                                inventory_line.product_qty != product_qty:
                            inventory_line.write({'product_qty': product_qty})
            del vals['line_ids']
        return super(StockInventory, self).write(vals)
