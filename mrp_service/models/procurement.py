# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# ajouter les fournisseurs sur les services


from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    # TODO rajouter un field pour dire que le production_id (mrp)
    # est en attente de nous et pas l'inverse ?

    @api.multi
    def _is_service_procurement(self):
        """Helper."""
        self.ensure_one()
        if self.product_id and self.product_id.type == 'service':
            tmpl = self.product_id.product_tmpl_id
            return tmpl.property_subcontracted_service
        return False

    @api.multi
    def _check(self):
        """Validate procurement if purchase of service is done."""
        if self._is_service_procurement():
            return (
                self.purchase_id and
                self.purchase_id.state in ['purchase', 'done']
            )
        return super(ProcurementOrder, self)._check()

    @api.multi
    def propagate_cancels(self):
        """Forbid procurement cancelation if production is already done."""
        result = super(ProcurementOrder, self).propagate_cancels()
        for procurement in self:
            if not procurement._is_service_procurement():
                continue
            if procurement.production_id.state == 'done':
                # utile ?
                raise UserError(
                    _('Can not cancel a procurement related to a produced manufacturing order.')
                )
            # import pdb
            # pdb.set_trace()
            # if procurement.rule_id.action == 'buy' and procurement.purchase_line_id:
            #     if procurement.purchase_line_id.order_id.state not in ('draft', 'cancel', 'sent', 'to validate'):
                   
            # if procurement.purchase_line_id:
           
        return result
        
    # @api.multi
    # def _run(self):
    #     if self.rule_id and self.rule_id.action == 'buy':
    #         import pdb
    #         pdb.set_trace()
    #     return super(ProcurementOrder, self)._run()
