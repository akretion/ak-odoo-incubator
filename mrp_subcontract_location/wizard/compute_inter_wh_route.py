# -*- coding: utf-8 -*-

from odoo import models


class ComputeInterwhRouteWizard(models.TransientModel):
    _name = 'compute.interwh.route.wizard'

    def recompute_wh_route_global(self):
        self.ensure_one()
        self.env['mrp.bom'].compute_product_routes_cron()
