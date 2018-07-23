# -*- coding: utf-8 -*-
# Copyright 2016-18 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# Copyright 2016 Aleph Objects, Inc. (https://www.alephobjects.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models, _
from datetime import timedelta
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, float_round
import operator as py_operator

_logger = logging.getLogger(__name__)


OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '==': py_operator.eq,
    '!=': py_operator.ne
}


UNIT = dp.get_precision('Product Unit of Measure')


_PRIORITY_LEVEL = [
    ('1_red', 'Red'),
    ('2_yellow', 'Yellow'),
    ('3_green', 'Green')
]


class StockWarehouseOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'
    _description = "Stock Buffer"

    @api.multi
    @api.depends("dlt")
    def _compute_procure_recommended_date(self):
        print "dans notre _compute_procure_recommended_date !!"
        for rec in self:
            rec.procure_recommended_date = \
                fields.date.today() + timedelta(days=int(rec.dlt))

    @api.multi
    @api.depends("procurement_ids", "minimum_order_quantity")
    def _compute_procure_recommended_qty(self):
        print "on devrait compter ici la minimum recomm qty!"

    def _get_manufactured_bom(self):
        return self.env['mrp.bom'].search(
            ['|',
             ('product_id', '=', self.product_id.id),
             ('product_tmpl_id', '=', self.product_id.product_tmpl_id.id),
             '|',
             ('location_id', '=', self.location_id.id),
             ('location_id', '=', False)], limit=1)

    def _compute_dlt(self):
        for rec in self:
            # TODO : prendre l'info sur la BOM si y'en a une ?
            # if rec.buffer_profile_id.item_type == 'manufactured':
            #     bom = rec._get_manufactured_bom()
            #     rec.dlt = bom.dlt
            # elif rec.buffer_profile_id.item_type == 'distributed':
            #     rec.dlt = rec.lead_days
            # else:
                rec.dlt = rec.product_id.seller_ids and \
                    rec.product_id.seller_ids[0].delay or rec.lead_days

    dlt = fields.Float(string="Decoupled Lead Time (days)",
                       compute="_compute_dlt")
    order_cycle = fields.Float(string="Minimum Order Cycle (days)")
    minimum_order_quantity = fields.Float(string="Minimum Order Quantity",
                                          digits=UNIT)
    qualified_demand = fields.Float(string="Qualified demand", digits=UNIT,
                                    readonly=True)
    incoming_dlt_qty = fields.Float(
        string="Incoming (Within DLT)",
        readonly=True,
    )
    planning_priority_level = fields.Selection(
        string="Planning Priority Level", selection=_PRIORITY_LEVEL,
        readonly=True)
    execution_priority_level = fields.Selection(
        string="On-Hand Alert Level",
        selection=_PRIORITY_LEVEL, store=True, readonly=True)
    # We override the calculation method for the procure recommended qty
    procure_recommended_qty = fields.Float(
        compute="_compute_procure_recommended_qty", store=True)
    procure_recommended_date = fields.Date(
        compute="_compute_procure_recommended_date")
    mrp_production_ids = fields.One2many(
        string='Manufacturing Orders', comodel_name='mrp.production',
        inverse_name='orderpoint_id')
    purchase_lines_ids = fields.One2many(
        string="Purchase Order Lines", comodel_name="purchase.order.line",
        inverse_name="orderpoint_id",
    )
    horizon = fields.Float(string="horizon", help="Number of day to look at")
    next_need = fields.Date()
    least_order_date = fields.Date()
    _order = 'planning_priority_level asc'

    @api.multi
    def _search_stock_moves_qualified_demand_domain(self):
        self.ensure_one()
        horizon = self.horizon
        date_to = fields.Date.to_string(fields.date.today() + timedelta(
            days=horizon))
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        return [('product_id', '=', self.product_id.id),
                ('state', 'in', ['waiting', 'confirmed', 'assigned']),
                ('location_id', 'in', locations.ids),
                ('location_dest_id', 'not in', locations.ids),
                ('date_expected', '<=', date_to)]

    @api.multi
    def _search_stock_moves_incoming_domain(self):
        self.ensure_one()
        horizon = self.horizon  # self.dlt or 0.0
        date_to = fields.Date.to_string(fields.date.today() + timedelta(
            days=horizon))
        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])])
        return [('product_id', '=', self.product_id.id),
                ('state', 'in', ['waiting', 'confirmed', 'assigned']),
                ('location_id', 'not in', locations.ids),
                ('location_dest_id', 'in', locations.ids),
                ('date_expected', '<=', date_to)]

    @api.multi
    def _calc_planning_priority(self):
        for rec in self:
            rec.refresh()
            if not rec.next_need:
                rec.planning_priority_level = '3_green'
                rec.least_order_date = fields.date.today() + timedelta(
                    days=int(rec.horizon))
                return
            diff = (
                fields.Datetime.from_string(rec.next_need).date() -
                fields.Datetime.from_string(rec.procure_recommended_date).date()
            ).days

            if diff < 0:
                rec.planning_priority_level = '1_red'
                rec.least_order_date = fields.date.today()
                return

            if (
                fields.Datetime.from_string(rec.next_need).date() <=
                fields.date.today() + timedelta(days=int(rec.horizon))
            ):
                rec.planning_priority_level = '2_yellow'
                rec.least_order_date = (
                    fields.Datetime.from_string(rec.next_need).date() -
                    timedelta(days=int(rec.dlt))
                )
            else:
                rec.planning_priority_level = '3_green'
                rec.least_order_date = fields.date.today() + timedelta(
                    days=int(rec.horizon))

    @api.multi
    def _calc_execution_priority(self):
        for rec in self:
            rec.execution_priority_level = '3_green'

    @api.multi
    def _calc_qualified_demand(self):
        for rec in self:
            rec.refresh()
            rec.qualified_demand = 0.0
            inc_domain = rec._search_stock_moves_incoming_domain()
            out_domain = rec._search_stock_moves_qualified_demand_domain()
            inc_moves = self.env['stock.move'].search(inc_domain)
            out_moves = self.env['stock.move'].search(out_domain)
            all_moves = inc_moves + out_moves
            demand_by_days = {}
            move_dates = [fields.Datetime.from_string(dt).date() for dt in
                          all_moves.mapped('date_expected')]
            for move_date in move_dates:
                demand_by_days[move_date] = {
                    'inc': 0.0, 'out': 0.0, 'sum': 0.0}
            for move in inc_moves:
                date = fields.Datetime.from_string(move.date_expected).date()
                demand_by_days[date]['inc'] += \
                    move.product_qty - move.reserved_availability
            for move in out_moves:
                date = fields.Datetime.from_string(move.date_expected).date()
                demand_by_days[date]['out'] -= move.product_qty

            demand_sorted = demand_by_days.keys()
            demand_sorted.sort()
            min_date = False
            sum_to_order = 0.0
            for i in xrange(len(demand_sorted)):
                day = demand_by_days[demand_sorted[i]]
                prev = demand_by_days[demand_sorted[max(i - 1, 0)]]
                day['sum'] = day['inc'] + day['out'] + prev['sum']
                #if date <= fields.date.today():
                rec.qualified_demand += demand_by_days[date]['inc']
                if not min_date:
                    if day['sum'] < 0:
                        min_date = demand_sorted[i]
                if day['sum'] < 0:
                    sum_to_order = sum_to_order + day['sum']
            rec.next_need = min_date
            rec.procure_recommended_qty = sum_to_order * -1
            print "sum to order : %s" % sum_to_order
        return True

    @api.multi
    def _calc_incoming_dlt_qty(self):
        for rec in self:
            rec.incoming_dlt_qty = 0.0
            domain = rec._search_stock_moves_incoming_domain()
            moves = self.env['stock.move'].search(domain)
            rec.incoming_dlt_qty = sum(moves.mapped('product_qty'))
        return True

    @api.multi
    def cron_actions(self):
        """This method is meant to be inherited by other modules in order to
        enhance extensibility."""
        self.ensure_one()
        self._calc_qualified_demand()
        self._calc_incoming_dlt_qty()
        self._calc_planning_priority()
        self._calc_execution_priority()
        self.mrp_production_ids._calc_execution_priority()
        self.purchase_lines_ids._calc_execution_priority()
        return True

    @api.model
    def cron_ddmrp(self, automatic=False):
        """calculate key DDMRP parameters for each orderpoint
        Called by cronjob.
        """
        _logger.info("Start cron_ddmrp.")
        orderpoints = self.search([])
        i = 0
        j = len(orderpoints)
        for op in orderpoints:
            i += 1
            _logger.debug("ddmrp cron: %s. (%s/%s)" % (op.name, i, j))
            try:
                op.cron_actions()
                if automatic:
                    self.env.cr.commit()
            except Exception:
                if automatic:
                    self.env.cr.rollback()
                    _logger.exception(
                        'Fail to create recurring invoice for orderpoint %s',
                        op.name)
                else:
                    raise
        _logger.info("End cron_ddmrp.")

        return True
