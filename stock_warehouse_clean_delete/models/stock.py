# -*- coding: utf-8 -*-
# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models


class AbstractUnlink(models.AbstractModel):
    _name = "abstract.unlink"
    _unlink_before = None
    _unlink_after = None

    def unlink(self):
        for record in self:
            for field_to_delete in self._unlink_before:
                if record[field_to_delete]:
                    record[field_to_delete].unlink()
        record_to_delete = set()
        for record in self:
            for field_to_delete in self._unlink_after:
                if record[field_to_delete]:
                    record_to_delete.add(record[field_to_delete])
        res = super(AbstractUnlink, self).unlink()
        for record in record_to_delete:
            if record.exists():
                record.unlink()
        return res


class StockWarehouse(models.Model):
    _inherit = ["stock.warehouse", "abstract.unlink"]
    _name = "stock.warehouse"

    _unlink_before = [
        'pick_type_id',
        'pack_type_id',
        'out_type_id',
        'in_type_id',
        'int_type_id',
    ]

    _unlink_after = [
        'view_location_id',
        'lot_stock_id',
        'wh_input_stock_loc_id',
        'wh_qc_stock_loc_id',
        'wh_output_stock_loc_id',
        'wh_pack_stock_loc_id',
        'crossdock_route_id',
        'reception_route_id',
        'delivery_route_id',
        ]

    def unlink(self):
        rules = self.env['procurement.rule'].search([
            ('warehouse_id', 'in', self.ids),
            ])
        rules.unlink()
        return super(StockWarehouse, self).unlink()


class StockPickingType(models.Model):
    _inherit = ["stock.picking.type", "abstract.unlink"]
    _name = "stock.picking.type"

    _unlink_before = []
    _unlink_after = [
        'sequence_id',
        ]
