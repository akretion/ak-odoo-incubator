# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    last_price_unit = fields.Text(
        string="Derniers prix de vente",
        compute="_compute_last_price_unit",
        help="Display the last 3 unit prices for this product/customer",
    )

    @api.depends("product_id", "order_id.partner_id")
    def _compute_last_price_unit(self):
        for line in self:
            price_per_date = []
            if line.order_id.partner_id and line.product_id:
                partner = line.order_id.partner_id.commercial_partner_id
                history_sol = self.env["sale.order.line"].search(
                    [
                        ("order_id.commercial_partner_id", "=", partner.id),
                        ("state", "in", ("sale", "done")),
                        ("order_id", "!=", line.order_id.id),
                        ("product_id", "=", line.product_id.id),
                        ("product_uom_qty", ">", 0.0),
                    ],
                    order="id desc",
                    limit=3,
                )
                price_per_date = [
                    (
                        sol.order_id.date_order,
                        sol.order_id.name,
                        sol.price_subtotal / sol.product_uom_qty,
                    )
                    for sol in history_sol
                ]
                if len(history_sol) < 3:
                    limit = 3 - len(history_sol)
                    history_lines = self.env["sale.price.customer.history"].search(
                        [
                            ("product_id", "=", line.product_id.id),
                            ("partner_id", "=", partner.id),
                        ],
                        order="date desc",
                        limit=limit,
                    )
                    price_per_date += [
                        (history.date, history.document_ref, history.price)
                        for history in history_lines
                    ]
            last_price_unit = ""
            for i, (date, ref, price) in enumerate(price_per_date):
                if i != 0:
                    last_price_unit += "\n"
                # Force french date format for first version, to be improved...
                last_price_unit += f"{date.strftime('%d/%m/%Y')} / {ref} : {price}"
            line.last_price_unit = last_price_unit
