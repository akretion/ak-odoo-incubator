# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# ajouter les fournisseurs sur les services

from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    mo_id = fields.Many2one(
        'mrp.production', 'Mo',
        compute='_calc_mo_id',
        store=True,
        readonly=True,
    )
    date_planned_start = fields.Datetime(
        string=u'Schedule start',
        help=u'Start date of the production order if any',
        related='mo_id.date_planned_start',
        track_visibility='onchange')

    date_planned_finished = fields.Datetime(
        string=u'Schedule end',
        help=u'End date of the production order if any',
        related='mo_id.date_planned_finished',
        track_visibility='onchange')

    @api.multi
    @api.depends('procurement_ids', 'procurement_ids.production_id')
    def _calc_mo_id(self):
        for rec in self:
            if rec._is_service_procurement():
                rec.mo_id = rec.procurement_ids.production_id

    @api.multi
    def _is_service_procurement(self):
        """Ensure the order line is a service procurement.

        It's tied to a procurement.
        The procurement is tied to one manufacturing order
        the product is a subcontracted_service

        Multiple procurements or MOs not implemented
        """
        self.ensure_one()
        is_service = False
        has_mo = False
        if self.product_id and self.product_id.type == 'service':
            tmpl = self.product_id.product_tmpl_id
            is_service = tmpl.property_subcontracted_service

        if is_service and self.procurement_ids:
            has_mo = len(self.procurement_ids.production_id) == 1
        return is_service and has_mo

    @api.multi
    def write(self, values):
        """postpone (manufacturing orders)
        when changing (order line).schedule date.

        Count the number of days the line is postponed.
        Add this count to mo.date_planned_start and mo.date_planned_finished.

        line.date_planned can be different than mo.date_planned_finished
        for instnace, it can be a date of picking out or picking in
        if it's managed by an incoterm

        # TODO @api.onchange ? instead of write ?
        """
        date_from_string = fields.Datetime.from_string
        if 'date_planned' not in values:
            return super(PurchaseOrderLine, self).write(values)
        for rec in self:
            if not rec.mo_id:
                continue
            prev_date_planned = date_from_string(rec.date_planned)
            next_date_planned = date_from_string(values['date_planned'])
            delta = next_date_planned - prev_date_planned
            _logger.info(
                'Changing MO date_planned_finished, +%s days'
                % delta)
            next_date_planned_start = (
                date_from_string(rec.mo_id.date_planned_start) + delta)
            next_date_planned_finished = (
                date_from_string(rec.mo_id.date_planned_finished) + delta)
            # if user had set both date_planned_* and date_planned
            # we assume there is no postpone to do
            rec.mo_id.date_planned_finished = values.get(
                'date_planned_finished', next_date_planned_finished)
            rec.mo_id.date_planned_start = values.get(
                'date_planned_start', next_date_planned_start)
        result = super(PurchaseOrderLine, self).write(values)

        return result



class Purchase(models.Model):
    _inherit = 'purchase.order'

    # TODO rajouter un field pour dire que le production_id (mrp)
    # est en attente de nous et pas l'inverse ?

    @api.depends('order_line.procurement_ids.production_id')
    def _compute_mo(self):
        for order in self:
            mos = self.env['mrp.production']
            for line in order.order_line:
                mos |= line.mo_id
            order.manufacture_ids = mos
            order.mo_count = len(mos)

    mo_count = fields.Integer(compute='_compute_mo', string='Manufacturing Orders', default=0)
    manufacture_ids = fields.Many2many('mrp.production', compute='_compute_mo', string='Manufacturing Orders', copy=False)

    @api.multi
    def action_view_mo(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        When only one found, show the picking immediately.
        '''
        action = self.env.ref('mrp.mrp_production_action')
        result = action.read()[0]

        #override the context to get rid of the default filtering on picking type
        result.pop('id', None)
        result['context'] = {}
        mo_ids = sum([order.manufacture_ids.ids for order in self], [])
        #choose the view_mode accordingly
        if len(mo_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, mo_ids)) + "])]"
        elif len(mo_ids) == 1:
            res = self.env.ref('mrp.mrp_production_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = mo_ids and mo_ids[0] or False
        return result

    @api.multi
    def button_approve(self, force=False):
        """Check procurement when PO is approved.

        Approved is after confirmed when 2-steps validiation."""
        res = super(Purchase, self).button_approve()
        for rec in self:
            if rec.state == 'purchase':
                for line in rec.order_line:
                    if line.mo_id:
                        line.procurement_ids.check()
        return res

    @api.multi
    def button_cancel(self):
        """Forbid PO canceling of done production."""
        for rec in self:
            for line in rec.order_line:
                if line.mo_id:
                    if line.mo_id.state == 'done':
                        raise UserError(
                            _('Unable to cancel purchase order %s as some \
                            productions have already been done.')
                            % (line.name))
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
                if line.mo_id:
                    line.procurement_ids.state = 'running'
