# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    def _update_delay(self):
        forced_company = False
        if self.env.context.get('force_company'):
            forced_company = self.env['res.company'].browse(
                self.env.context.get('force_company'))
        for suppinfo in self:
            products = suppinfo.product_id or \
                       suppinfo.product_tmpl_id.product_variant_ids

            company = suppinfo.company_id or forced_company or \
                      self.env.user.company_id
            limit = company.incoming_shippment_number_delay or 3
            self.env.cr.execute("""
                SELECT po.date_approve, pi.date_done
                FROM stock_move m
                    JOIN stock_picking pi ON pi.id = m.picking_id
                    JOIN stock_picking_type t ON t.id = pi.picking_type_id
                    JOIN purchase_order_line l ON l.id = m.purchase_line_id
                    JOIN purchase_order po ON po.id = l.order_id
                WHERE m.product_id in %s AND t.code = 'incoming'
                    AND m.state = 'done'
                GROUP BY po.date_approve, pi.date_done
                ORDER BY pi.date_done desc
                LIMIT %s
            """, (tuple(products.ids), limit))
            dates = self.env.cr.fetchall()
            if not dates:
                continue
            delays = []
            for delay_info in dates:
                if not delay_info[0] or not delay_info[1]:
                    continue
                date_approve = datetime.strptime(
                        delay_info[0], DEFAULT_SERVER_DATETIME_FORMAT).date()
                date_done = datetime.strptime(
                        delay_info[1], DEFAULT_SERVER_DATETIME_FORMAT).date()
                delays.append((date_done - date_approve).days)
            if not delays:
                continue
            delay = int(round(float(sum(delays))/len(delays)))
            if suppinfo.delay != delay:
                suppinfo.write({'delay': delay})
