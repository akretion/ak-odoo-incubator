# -*- coding: utf-8 -*-
# Copyright (C) 2017 Akretion (<http://www.akretion.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models
from openerp.osv import fields as old_fields


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Native method is very long, juste replace by sql
    def _sales_count(self, cr, uid, ids, field_name, arg, context=None):
        r = dict.fromkeys(ids, 0)
        user = self.pool['res.users'].browse(cr, uid, uid)
        for product_id in ids:
            cr.execute("""
                SELECT sum(product_uom_qty)
                FROM sale_report r
                WHERE product_id = %s
                    AND state in ('confirmed', 'done')
                    AND company_id = %s
            """, (product_id, user.company_id.id,))
            tot = cr.fetchall()
            r[product_id] = tot and tot[0][0] or 0
        return r

    # Just put the same that in native module.
    # On migration, no need to do it, juste surcharge the compute method
    _columns = {
        'sales_count': old_fields.function(
            _sales_count,
            string='# Sales',
            type='integer'),
    }
