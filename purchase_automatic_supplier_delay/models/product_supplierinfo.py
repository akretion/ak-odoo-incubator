# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo import models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    def _update_delay(self):
        for suppinfo in self:
            products = (
                suppinfo.product_id or suppinfo.product_tmpl_id.product_variant_ids
            )

            company = suppinfo.company_id or self.env.company
            limit = company.incoming_shipment_number_delay or 3
            self.flush()
            self.env.cr.execute(
                """
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
            """,
                (tuple(products.ids), limit),
            )
            dates = self.env.cr.fetchall()
            if not dates:
                continue
            delays = []
            for delay_info in dates:
                if not delay_info[0] or not delay_info[1]:
                    continue
                date_approve = delay_info[0].date()
                date_done = delay_info[1].date()
                delays.append((date_done - date_approve).days)
            if not delays:
                continue
            delay = int(round(float(sum(delays)) / len(delays)))
            if suppinfo.delay != delay:
                suppinfo.write({"delay": delay})
