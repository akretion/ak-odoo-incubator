# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import api, fields, models
_logger = logging.getLogger(__name__)


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    is_buffered = fields.Boolean(
        string="Buffered?", compute="_compute_is_buffered",
        help="True when the product has an DDMRP buffer associated.",
    )
    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint', string='Orderpoint',
        compute="_compute_is_buffered",
    )
    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        compute="_compute_dlt",
        store=True,
    )
    mlt = fields.Float(
        string="Max lead Time",
        compute="_compute_dlt",
        store=True,
)
    has_mto_rule = fields.Boolean(
        string="MTO",
        help="Follows an MTO Pull Rule",
        compute="_compute_mto_rule",
    )

    def _get_search_buffer_domain(self):
        product = self.product_id or \
            self.product_tmpl_id.product_variant_ids[0]
        domain = [('product_id', '=', product.id)]
        if self.location_id:
            domain.append(('location_id', '=', self.location_id.id))
        return domain

    def _compute_is_buffered(self):
        for bom in self:
            domain = bom._get_search_buffer_domain()
            orderpoint = self.env['stock.warehouse.orderpoint'].search(
                domain, limit=1)
            bom.orderpoint_id = orderpoint
            bom.is_buffered = True if orderpoint else False

    def _compute_mto_rule(self):
        for rec in self:
            # template = rec.product_id.product_tmpl_id
            # or rec.product_tmpl_id
            rec.has_mto_rule = True
            # True if (
            #    rec.location_id in
            #    template.mrp_mts_mto_location_ids) else False

    @api.multi
    def _get_longest_path(self):
        if not self.bom_line_ids:
            return 0.0
        paths = [0] * len(self.bom_line_ids)
        paths_mlt = []
        i = 0
        for line in self.bom_line_ids:
            if line.is_buffered:
                i += 1
            else:
                paths[i] = line.dlt
                i += 1
            paths_mlt.append(line.mlt)
        self.mlt += max(paths_mlt)
        return max(paths)

    @api.multi
    def _get_manufactured_dlt(self):
        """Computes the Decoupled Lead Time exploding all the branches of the
        BOM until a buffered position and then selecting the greatest."""
        self.ensure_one()
        dlt = self.product_id.produce_delay or \
            self.product_tmpl_id.produce_delay
        self.mlt = self.product_id.produce_delay or \
            self.product_tmpl_id.produce_delay
        dlt += self._get_longest_path()
        return dlt

    @api.depends(
        'product_id.produce_delay',
        'product_tmpl_id.produce_delay',
        'bom_line_ids.dlt',
        'bom_line_ids.mlt')
    def _compute_dlt(self):
        for rec in self:
            _logger.info("bom.compute_dlt")
            rec.dlt = rec._get_manufactured_dlt()


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    is_buffered = fields.Boolean(
        string="Buffered?", compute="_compute_is_buffered",
        help="True when the product has an DDMRP buffer associated.",
    )
    orderpoint_id = fields.Many2one(
        comodel_name='stock.warehouse.orderpoint', string='Orderpoint',
        compute="_compute_is_buffered",
    )
    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        compute='_compute_dlt',
        store=True,
    )
    mlt = fields.Float(
        string="Maximum Lead Time (days)",
        store=True,
        compute="_compute_mlt")
    has_mto_rule = fields.Boolean(
        string="MTO",
        help="Follows an MTO Pull Rule",
        compute="_compute_mto_rule",
    )

    def _get_search_buffer_domain(self):
        product = self.product_id or \
            self.product_tmpl_id.product_variant_ids[0]
        domain = [
            ('product_id', '=', product.id),
        ]
        if self.bom_id.location_id:
            domain.append(('location_id', '=', self.bom_id.location_id.id))
        return domain

    def _compute_is_buffered(self):
        for line in self:
            # fix raph
            domain = line._get_search_buffer_domain()
            orderpoint = self.env['stock.warehouse.orderpoint'].search(
                domain, limit=1)
            line.orderpoint_id = orderpoint
            line.is_buffered = True if orderpoint else False

    def _compute_mto_rule(self):
        for rec in self:
            rec.has_mto_rule = True
            # True if (
            #    rec.location_id in
             #   rec.product_id.mrp_mts_mto_location_ids) else False

    @api.depends('product_id.dlt')
    def _compute_dlt(self):
        for rec in self:
            rec.dlt = rec.product_id.dlt

    @api.depends('product_id.mlt')
    def _compute_mlt(self):
        for rec in self:
            rec.mlt = rec.product_id.mlt
