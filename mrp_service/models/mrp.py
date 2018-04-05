# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# ajouter les fournisseurs sur les services


from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    """ Defines bills of material for a product or a product template """
    _inherit = 'mrp.bom'

    # ajouter un type ?

    # ça peut être une variante ?
    service_id = fields.Many2one(
        'product.product', 'Service',
        domain="[('type', 'in', ['service'])]")


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    service_id = fields.Many2one(
        'product.product',
        'Service',
        readonly=True,
        compute="_compute_service_id",
    )

    def _compute_service_id(self):
        for rec in self:
            rec.service_id = rec.bom_id.service_id.id

    @api.model
    def create(self, values):
        production = super(MrpProduction, self).create(values)
        production._generate_service_procurement()
        return production

    @api.multi
    def _generate_service_procurement(self):
        if not self.service_id:
            return
        _logger.info('on va generer des procurements')

        procurements = self.env['procurement.order']
        for rec in self:
            vals = rec._prepare_procurement_for_service()
            procurements |= procurements.create(vals)
        if procurements:
            procurements.run()
        import pdb
        pdb.set_trace()


    def _prepare_procurement_for_service(self):
        return {
            'name': "/",
            'origin': self.name,
            'company_id': self.company_id.id,
            'date_planned': self.date_planned_start,
            'product_id': self.service_id.id,
            'product_qty': self.product_qty,
            'product_uom': self.service_id.uom_po_id.id,
            'location_id': self.location_dest_id.id,
            'move_dest_id': (
                self.procurement_ids and
                self.procurement_ids[0].move_dest_id.id or False),
            'group_id': self.procurement_group_id.id,
            #'route_ids': [], #[(4, x.id) for x in self.route_ids],
            'warehouse_id': (
                self.picking_type_id and
                self.picking_type_id.warehouse_id.id or False),
            'priority': self.priority,
        }
