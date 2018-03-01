# coding: utf-8
# © 2018 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields, _
import openerp.addons.decimal_precision as dp


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    calc_product_cost = fields.Float(
        compute='_compute_product_cost', string='Computed cost',
        digits_compute=dp.get_precision('Account'))
    manual_product_cost = fields.Float(
        string='Manual cost',
        digits_compute=dp.get_precision('Account'))
    value = fields.Float(
        compute='_compute_value', string='Value',
        digits_compute=dp.get_precision('Account'))
    cost_explanation = fields.Text(
        compute='_compute_product_cost',
        help='Explain computation method for each product')

    @api.multi
    @api.depends('product_id',)
    def _compute_product_cost(self):
        inv_l_obj = self.env['account.invoice.line']
        po_l_obj = self.env['purchase.order.line']
        for invent_line in self:
            # get cost form supplier invoice
            explanation = ''
            cost_price = 0
            if not invent_line.product_id:
                continue
            inv_line = inv_l_obj.search(
                [('product_id', '=', invent_line.product_id.id),
                 ('invoice_id.type', '=', 'out_invoice'),
                 ('invoice_id.state', 'in', ('open', 'paid')),
                 ], limit=1)
            if inv_line:
                cost_price = inv_line.price_unit
                explanation = _('Cost from Invoice %s') %\
                    inv_line.invoice_id.number
            if not cost_price:
                # get cot price form purchase
                po_line = po_l_obj.search(
                    [('product_id', '=', invent_line.product_id.id),
                     ('order_id.state', '=', 'done')
                     ], limit=1)
                if po_line:
                    cost_price = po_line.price_unit
                    explanation = _('Cost from Purchase %s') %\
                        po_line.order_id.name
            if not cost_price:
                # get cot price form supplier info
                sup_info = invent_line.product_id.seller_ids
                if sup_info and sup_info[0].pricelist_ids:
                    cost_price = sup_info[0].pricelist_ids[0].price
                    explanation = _('Cost from supplier info %s') %\
                        sup_info[0].name.name
            if not cost_price:
                # get cot price form supplier info
                sup_info = invent_line.product_id.seller_id
                if invent_line.product_id.standard_price:
                    cost_price = invent_line.product_id.standard_price
                    explanation = _('Cost from product "%s" standard_price') %\
                        invent_line.product_id.default_code or\
                        invent_line.product_id.name
            if not cost_price:
                explanation = _('Not Cost found for the product "%s"') %\
                    invent_line.product_id.default_code or\
                    invent_line.product_id.name
            invent_line.calc_product_cost = cost_price
            invent_line.cost_explanation = explanation

    @api.multi
    @api.depends('calc_product_cost', 'manual_product_cost')
    def _compute_value(self):
        for line in self:
            if line.manual_product_cost:
                line.value = line.manual_product_cost * line.product_qty
            else:
                line.value = line.calc_product_cost * line.product_qty
