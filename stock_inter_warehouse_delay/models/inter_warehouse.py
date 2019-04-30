# -*- coding: utf-8 -*-
# Copyright 2019 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class InterWarehouseDelay(models.Model):
    _name = 'stock.inter_warehouse_delay'
    _order = 'source_wh_id, dest_wh_id asc'

    source_wh_id = fields.Many2one('stock.warehouse')
    dest_wh_id = fields.Many2one('stock.warehouse')
    delay = fields.Integer()

    _sql_constraints = [
        ('uniq_delay',
         'unique(source_wh_id, dest_wh_id)',
         'There should be one record between two warehouses'),
    ]

    @api.multi
    def write(self, vals):
        res = super(InterWarehouseDelay, self).write(vals)
        self._update_delay()
        return res

    @api.multi
    def _update_delay(self):
        for rec in self:
            rules = self.env['procurement.rule'].search(
                rec._prepare_search_rule())
            rules.write({'delay': rec.delay})

    def _prepare_search_rule(self):
        sender = self.source_wh_id
        picking_type_out = sender.out_type_id
        return [
            ('warehouse_id', '=', sender.id),
            ('picking_type_id', '=', picking_type_out.id),
            ('partner_address_id', '=', self.dest_wh_id.partner_id.id),
        ]
