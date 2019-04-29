# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dlt = fields.Float(related='product_variant_ids.dlt')
    mlt = fields.Float(related='product_variant_ids.mlt')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        compute="_compute_dlt",
        store=True,
    )
    mlt = fields.Float(
        string="Max lead time (days)",
        compute="_compute_dlt",
        store=True)

    @api.depends(
        'seller_ids.delay',
        'bom_ids.dlt',
        'bom_ids.mlt',
    )
    def _compute_dlt(self):
        for rec in self:
            _logger.info("product.compute_dlt id: %s" % rec.id or '?')
            if rec.bom_ids:
                rec.dlt = rec.bom_ids[0].dlt
                rec.mlt = rec.bom_ids[0].mlt
            else:
                rec.dlt = rec.seller_ids and \
                    rec.seller_ids[0].delay or 0.0
                rec.mlt = rec.seller_ids and \
                    rec.seller_ids[0].delay or 0.0
