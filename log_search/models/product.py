# coding: utf-8
# © 2015  Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import json
import datetime
from openerp import models, api

_logger = logging.getLogger('log_search')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name=None, args=None, operator='ilike', limit=100):
        res = super(ProductProduct, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        _logger.info(json.dumps({
            "uid": self._context['uid'],
            "date": datetime.datetime.now().isoformat(),
            "method": "name_search",
            "value": name,
            "count": len(res),
            "op": operator,
        }))
        return res

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None,
                    order=None):
        res = super(ProductProduct, self).search_read(
            domain=domain, fields=fields, offset=offset,
            limit=limit, order=order)
        _logger.info(json.dumps({
            "uid": self._context['uid'],
            "date": datetime.datetime.now().isoformat(),
            "method": "search_read",
            "value": domain,
            "count": len(res),
        }))
        return res
