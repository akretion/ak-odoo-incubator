# -*- coding: utf-8 -*-
# Copyright 2019 Raphael Reverdy Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import timedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    _logger.debug('Cannot import networkx lib')

# TODO:
# verifier facteur
# calculer forcasted_qty en stocké en même temps
# que procure_qty


class Forcast(models.Model):
    _name = 'stock.orderpoint.forcast'

    orderpoint_id = fields.Many2one(
        'stock.warehouse.orderpoint',)
    date = fields.Date()
    qty = fields.Float()

    @api.model
    def generate_forcast(self):
        """Generate forcast for all the orderpoints.

        Return a recordset of forcasts

        Not implemented yet :
            * MoQ of orderpoints
            * Min/Max of orderpoints
        """
        # clean up
        Forcast = self.env['stock.orderpoint.forcast']
        rows = Forcast.search([])
        rows.unlink()
        orderpoints = self.env['stock.warehouse.orderpoint'].search([])
        orderpoints_by_product = {
            op.product_id.product_tmpl_id.id: op
            for op in orderpoints
        }
        forcasts = Forcast.browse(False)
        for op in orderpoints:
            # refresh procure_recommended_qty without forcasts
            op._calc_qualified_demand()  # TODO put it ouside loop and fix api.multi

        for op in orderpoints:
            qty = op.procure_recommended_qty
            if not qty:
                continue
            date = op.least_order_date  # ou recommanded_date ?
            prod = op.product_id.product_tmpl_id
            todo = self.env['stock.orderpoint.forcast.table'].search(
                [['finished_product_tmpl_id', '=', prod.id]])
            for row in todo:
                vals = self._prepare_forcast(
                    orderpoints_by_product, row, qty, date)
                forcasts |= Forcast.create(vals)
        return forcasts

    def _prepare_forcast(self, orderpoints_by_product, row, qty, date):
        row_material = row.raw_material_product_tmpl_id.id
        return {
            'orderpoint_id': orderpoints_by_product[row_material].id,
            'qty': row.factor * qty,
            'date': fields.Date.to_string(
                fields.Date.from_string(date) +
                timedelta(days=int(row.delay))
            ),
        }


class ForcastTable(models.Model):
    _name = 'stock.orderpoint.forcast.table'

    finished_product_tmpl_id = fields.Many2one(
        'product.template')
    raw_material_product_tmpl_id = fields.Many2one(
        'product.template')
    delay = fields.Float(string='delay')
    factor = fields.Float(string='factor')

    def _prepare_table_row(self, row):
        return {
            'finished_product_tmpl_id': row['dst'],
            'raw_material_product_tmpl_id': row['src'],
            'delay': row['delay'],
            'factor': row['qty'],
        }

    @api.model
    def build_forcast_table(self):
        graph = self._build_graph()
        buffers = self._get_buffers()
        pairs = self._detect_pairs(buffers, graph)
        table = self._build_convert_table(pairs, buffers, graph)

        # clean up
        rows = self.env['stock.orderpoint.forcast.table'].search([])
        rows.unlink()
        # fill in
        for row in table:
            vals = self._prepare_table_row(row)
            self.env['stock.orderpoint.forcast.table'].create(vals)

    def _get_buffers(self):
        """buffuerized product tmpl id."""
        return (
            self.env['stock.warehouse.orderpoint']
            .search([])
            .mapped('product_id.product_tmpl_id.id')
        )

    def _build_graph(self):
        g = nx.DiGraph()
        # it's directed and disconnected graph
        bom_lines = self.env['mrp.bom.line'].search([])

        for line in bom_lines:
            a = line.product_id.product_tmpl_id.id
            b = line.bom_id.product_tmpl_id.id
            w = line.dlt
            f = line.product_qty
            g.add_edge(
                a, b,
                delay=w,
                factor=f,
            )
        return g

# g = nx.DiGraph()
# g.add_edge('x1', 'y1', delay=1, factor=0.5,)
# g.add_edge('x2', 'y1', delay=2, factor=1,)
# g.add_edge('y1', 'z', delay=8, factor=1,)
# g.add_edge('x1', 'y2', delay=1, factor=1,)
# g.add_edge('y2', 'z', delay=8, factor=1,)
# g.add_edge("x1", "z", delay=4, factor=1)
# buffers = ('z', 'x1', 'y2')
#         # Racines : out_degree = 0
#         # Feuilles : in_degree = 0

#         # on veut tous les buffers qui sont connectés entre eux


    def _build_convert_table(self, to_visit, buffers, graph):
        """
        Calculate the delays and the factors between two bufferized products
        in a bom.

        delay : it's the sum of decoupled lead times on the path
        factor: it's the factor of qty on the path

        to_visit: an array of matrial / finish product
        buffers: an array of all product bufferized 
        @returns: an array of { src, dst, qty, delay }
        ."""
        b2b = []

        def visit(source, parent, target, sum_qty=1, sum_delay=0):
            """Will go from source to target and return
            the sum of delays and sum of qty

            should be initiated with
            visit(src, src, dst)

            it can have multiple src, dst if there is multiple
            paths in the graph : a raw material appear on multiple levels
            It fills in the variable b2b
            """
            for node in graph[parent]:
                edge = graph[parent][node]
                # TODO: convertir des unités
                qty = edge['factor'] * sum_qty
                delay = edge['delay'] + sum_delay
                if target == node:
                    b2b.append({
                        'src': source,
                        'dst': target,
                        'qty': qty,
                        'delay': delay})
                #elif node in buffers:
                #    # no need to continue further this path
                #    continue
                else:
                    visit(source, node, target, qty, delay)

        for (src, dst) in to_visit:
            visit(src, src, dst)
        return b2b

    def _detect_pairs(self, buffers, graph):
        """
        buffers is an array of all order points
        graph is mostly the BOM tree

        Returns an array of tuples (raw -> finished)
        ."""

        def visit(parent):
            """Etablish (raw prod -> finsihed prod) paths.

            Find connected (even indirectly or multiple) buffered products
            From raw material of raw material to finished product
            """
            for n in graph[parent]:
                if n in buffers:
                    to_visit.add((source, n))  # skip duplicate
                else:
                    visit(n)

        to_visit = set()
        for buffered in buffers:
            source = buffered
            if graph.has_node(source):
                # we don't need to propagate anything
                # if product is buy
                visit(buffered)
        return [(src, dst) for (src, dst) in list(to_visit)]
