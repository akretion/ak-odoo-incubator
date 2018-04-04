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
        'product.template', 'Service',
        domain="[('type', 'in', ['service'])]")


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    service_id = fields.Many2one(
        'product.template',
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
        self._generate_service_procurement()
        return production

    def _generate_service_procurement(self):
        if not self.service_id:
            return
        _logger.info('on va generer des procurements')

