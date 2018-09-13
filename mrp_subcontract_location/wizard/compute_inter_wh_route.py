# -*- coding: utf-8 -*-

from odoo import models


class ComputeInterwhRouteWizard(models.TransientModel):
    _name = 'compute.interwh.route.wizard'

    def recompute_wh_route_global(self):
        self.ensure_one()
        boms = self.env['mrp.bom'].search([])
        boms.check_and_set_product_routes()
