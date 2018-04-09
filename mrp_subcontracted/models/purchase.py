# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# ajouter les fournisseurs sur les services


from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def _is_service_procurement(self):
        self.ensure_one()
        if self.product_id and self.product_id.type == 'service':
            tmpl = self.product_id.product_tmpl_id
            return tmpl.property_subcontracted_service
        return False


class Purchase(models.Model):
    _inherit = 'purchase.order'

    # TODO rajouter un field pour dire que le production_id (mrp)
    # est en attente de nous et pas l'inverse ?

    @api.multi
    def button_approve(self, force=False):
        """Check procurement when PO is approved.

        Approved is after confirmed when 2-steps validiation."""
        res = super(Purchase, self).button_approve()
        for rec in self:
            if rec.state == 'purchase':
                for line in rec.order_line:
                    if line._is_service_procurement():
                        line.procurement_ids.check()
        return res

    @api.multi
    def button_cancel(self):
        """Forbid PO canceling of done production."""
        for rec in self:
            for line in rec.order_line:
                if line._is_service_procurement():
                    if line.procurement_ids.production_id.state == 'done':
                        raise UserError(
                            _('Unable to cancel purchase order %s as some productions have already been done.') % (line.name))
        super(Purchase, self).button_cancel()
        # ça passe en exception si rule.progate = false

    @api.multi
    def button_draft(self):
        """Put procurement back in running.

        When PO is canceled the procurment goes in exception.
        When PO is back to draft the procurement goes in running"""
        super(Purchase, self).button_draft()
        for rec in self:
            for line in rec.order_line:
                if line._is_service_procurement():
                    line.procurement_ids.state = 'running'
