# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dlt = fields.Float(related='product_variant_ids.dlt')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    dlt = fields.Float(
        string="Decoupled Lead Time (days)",
        compute="_compute_dlt",
        store=True,
    )

    @api.depends(
        'seller_ids.delay',
        'bom_ids.dlt', 'produce_delay', 'product_tmpl_id.produce_delay'
    )
    def _compute_dlt(self):
        for rec in self:
            _logger.info("product.compute_dlt")
            if rec.bom_ids:
                rec.dlt = rec.bom_ids[0].dlt
            else:
                rec.dlt = rec.seller_ids and \
                    rec.seller_ids[0].delay or 0.0
