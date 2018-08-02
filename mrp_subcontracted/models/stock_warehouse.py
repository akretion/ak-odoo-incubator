# -*- coding: utf-8 -*-

from odoo import api, models


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    # As we handle subcontractor, warehouse may belong to a supplier but we
    # may buy classic products to these supplier and need the normal supplier
    # location on supplier, not the transit location.
    # TODO handle case if partner is supplier or not?
    @api.model
    def _update_partner_data(self, partner_id, company_id):
        return
#        if partner_id:
#            partner = self.env['res.partner'].browse(partner_id)
#            if partner.supplier:
#                return
#        return super(StockWarehouse, self)._update_partner_data(
#            partner_id, company_id)
