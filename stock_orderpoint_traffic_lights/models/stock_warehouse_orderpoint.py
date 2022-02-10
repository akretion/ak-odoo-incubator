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

    def _compute_dlt(self):
        for rec in self:
            # product_id est calculé en fonction de sa BOM
            # TODO: ajouter le temps de transport en partant
            # de product_id.transit(rec.location_id)
            rec.dlt = rec.product_id.dlt # + rec.transit_to(rec.warehouse_id)

    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        # TODO mettre en releated
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
    net_flow_position = fields.Float(
        string="Net flow position", digits=UNIT,
        readonly=True)
    planning_priority_level = fields.Selection(
        string="Planning Priority Level", selection=_PRIORITY_LEVEL,
        readonly=True)
    execution_priority_level = fields.Selection(
        string="On-Hand Alert Level",
        selection=_PRIORITY_LEVEL, store=True, readonly=True)
    product_location_qty_available_not_res = fields.Float(
        # rename string from stock_warehouse_orderpoint_stock_info_unreserved
        string='On-Hand',
        help='Quantity On Location (Unreserved)',  # previsous name
    )
    on_hand_percent = fields.Float(string="On Hand/TOR (%)",
        store=True, readonly=True)
    # We override the calculation method for the procure recommended qty
    procure_recommended_qty = fields.Float(
        compute="_compute_procure_recommended_qty", store=True)
    procure_recommended_date = fields.Date(
        compute="_compute_procure_recommended_date")
    mrp_production_ids = fields.One2many(
        string='Manufacturing Orders', comodel_name='mrp.production',
        inverse_name='orderpoint_id')

    horizon = fields.Float(string="horizon", help="Number of day to look at")
    # TODO: faire la difference entre l'horizon
    # pour capter les besoins futurs
    next_need = fields.Date(readonly=True)
    least_order_date = fields.Date(readonly=True)
    forcasted_qty = fields.Float(compute='_calc_forcast')
    _order = 'planning_priority_level asc'

    @api.multi
    def _search_open_stock_moves_domain(self):
        self.ensure_one()
        return [('product_id', '=', self.product_id.id),
                ('state', 'in', ['draft', 'waiting', 'confirmed',
                                 'assigned']),
                ('location_dest_id', '=', self.location_id.id)]

    @api.multi
    def open_moves(self):
        self.ensure_one()
        # Utility method used to add an "Open Moves" button in the buffer
        # planning view
        domain = self._search_open_stock_moves_domain()
        records = self.env['stock.move'].search(domain)
        return self._stock_move_tree_view(records)

    @api.model
    def _stock_move_tree_view(self, lines):
        views = []
        tree_view = self.env.ref('stock.view_move_tree', False)
        if tree_view:
            views += [(tree_view.id, 'tree')]
        form_view = self.env.ref(
            'stock.view_move_form', False)
        if form_view:
            views += [(form_view.id, 'form')]

        return {
            'name': _('Non-completed Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.move',
            'view_type': 'form',
            'views': views,
            'view_mode': 'tree,form',
            'domain': str([('id', 'in', lines.ids)]),
        }

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
    def _calc_net_flow_position(self):
        for rec in self:
            rec.net_flow_position = \
                rec.product_location_qty_available_not_res + \
                rec.incoming_dlt_qty - rec.qualified_demand
            # on a desactivé top_of_green
            # usage = 0.0
            # if rec.top_of_green:
            #     usage = round(
            #         (rec.net_flow_position / rec.top_of_green*100), 2)
            # rec.net_flow_position_percent = usage
        return True

    @api.multi
    def _calc_planning_priority(self):
        # grosse divergence avec ddmrp
        for rec in self:
            rec.refresh()
            if not rec.next_need:
                # Even if we do not have next need, we may want to puchase to
                # respect the min/max quantities
                if rec.procure_recommended_qty > 0.0:
                    rec.planning_priority_level = '2_yellow'
                    rec.least_order_date = fields.date.today()
                else:
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
        # grosse divergence
        for rec in self:
            rec.execution_priority_level = '3_green'

    @api.multi
    def _calc_qualified_demand(self):
        # grosse différence avec ddmrp

        # todo: substract_procurements_from-orderoints
        # tenir compte de quand ces procurements vont arriver
        subtract_qty = self.subtract_procurements_from_orderpoints()
        for rec in self:
            rec.refresh()
            inc_domain = rec._search_stock_moves_incoming_domain()
            out_domain = rec._search_stock_moves_qualified_demand_domain()
            inc_moves = self.env['stock.move'].search(inc_domain)
            out_moves = self.env['stock.move'].search(out_domain)
            all_moves = inc_moves + out_moves
            forcasts = rec._forcast_needs()
            demand_by_days = {}
            qualified_demand = 0.0

            move_dates = [
                fields.Date.from_string(dt)
                for dt in (
                    all_moves.mapped('date_expected') +
                    forcasts.mapped('date')
                )]

            for move_date in move_dates:
                demand_by_days[move_date] = {
                    'inc': 0.0, 'out': 0.0, 'sum': 0.0, 'ideal': 0}
            for move in inc_moves:
                date = fields.Date.from_string(move.date_expected)
                demand_by_days[date]['inc'] += \
                    move.product_qty - move.reserved_availability
            for move in out_moves:
                date = fields.Date.from_string(move.date_expected)
                demand_by_days[date]['out'] -= move.product_qty
            for forcast in forcasts:
                print 'on ajoute un besoin de %s' % forcast.qty
                date = fields.Date.from_string(forcast.date)
                demand_by_days[date]['out'] -= forcast.qty

            demand_sorted = demand_by_days.keys()
            demand_sorted.sort()
            min_date = False  # when stock will be negative for the first time
            interval_to_look_at = (demand_sorted or [None])[-1]
            # how many days we want to procure after min_date
            # it will be fixed when min_date is set
            ideal_order_qty = 0.0
            # ideal_order_quantity: current_stock + ideal_order_qty should be
            # enough to cover the needs until min_date + interval_to_look_at
            # it's mainly procurement_qty

            already_in_stock = rec.with_context(
                location=rec.location_id.id
            ).product_id.qty_available
            incoming = subtract_qty[rec.id]
            future_stock = already_in_stock + incoming
            # future stock is what we will have if we do nothing

            if len(demand_sorted) > 0:
                demand_by_days[demand_sorted[0]]['sum'] = future_stock
                # we initate with qty in stock and qty to come
                # TODO:put substract_qty on the good dates instead of beggining
            else:
                future_stock_ideal = future_stock
            for i in xrange(len(demand_sorted)):
                current_date = demand_sorted[i]
                day = demand_by_days[demand_sorted[i]]
                prev = demand_by_days[demand_sorted[max(i - 1, 0)]]
                day['sum'] = day['inc'] + day['out'] + prev['sum']
                day['ideal'] = day['inc'] + day['out'] + prev['ideal'] + prev['sum']

                qualified_demand += day['out'] * -1
                if not min_date:
                    if day['sum'] < 0:
                        min_date = current_date
                        interval_to_look_at = (
                            min_date + timedelta(days=rec.order_cycle))
                if current_date <= interval_to_look_at:
                    if day['ideal'] < 0:
                        # day['ideal'] < 0 instead of < rec.product_min_qty
                        # because it's ok to take in safety stock
                        ideal_order_qty += day['ideal'] * -1
                        day['ideal'] = 0  # we cover only the need of the day
                    future_stock_ideal = day['ideal']
                    # future_stock_ideal is what will I have in stock
                    # if I order ideal_order_qty now

            product_qty = 0.0
            # we need to order something if ideal_qty_order > 0
            # OR we are under min buffer limit
            # in both cases we should refill up to max
            if float_compare(
                future_stock_ideal, rec.product_min_qty,
                precision_rounding=rec.product_uom.rounding
            ) < 0 or ideal_order_qty > 0:
                max_limit = max(rec.product_min_qty, rec.product_max_qty)
                sum_to_order = max(max_limit, ideal_order_qty)
                product_qty = self._calc_qty_from_uom(sum_to_order)
            rec.procure_recommended_qty = product_qty
            rec.next_need = min_date
            rec.qualified_demand = qualified_demand
            print "sum to order : %s" % product_qty
        return True

    def _calc_qty_from_uom(self, sum_to_order):
        if self.qty_multiple > 0:
            reste = sum_to_order % self.qty_multiple
        else:
            reste = 0.0
        if self.procure_uom_id:
            rounding = self.procure_uom_id.rounding
        else:
            rounding = self.product_uom.rounding
        if float_compare(
                reste, 0.0,
                precision_rounding=rounding) > 0:
            sum_to_order += self.qty_multiple - reste
        if self.procure_uom_id:
            product_qty = self.product_id.uom_id._compute_quantity(
                sum_to_order, self.procure_uom_id)
        else:
            product_qty = sum_to_order
        return product_qty

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
        self._calc_net_flow_position()
        self._calc_incoming_dlt_qty()
        self._calc_planning_priority()
        self._calc_execution_priority()
        self.mrp_production_ids._calc_execution_priority()
        self.mapped('purchase_line_ids')._calc_execution_priority()
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
        self.env['stock.orderpoint.forcast.table'].build_forcast_table()
        self.env['stock.orderpoint.forcast'].generate_forcast()

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

    def _forcast_needs(self):
        return self.env['stock.orderpoint.forcast'].search(
            [['orderpoint_id', '=', self.id]])

    @api.multi
    def _calc_forcast(self):
        for rec in self:
            rec.forcasted_qty = sum(rec._forcast_needs().mapped('qty'))
