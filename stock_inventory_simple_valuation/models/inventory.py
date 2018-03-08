# coding: utf-8
# © 2018 Mourad El Hadj Mimoun @ Akretion
# © 2018 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

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
    cost_origin = fields.Text(
        compute='_compute_product_cost',
        help='Explain computation method for each product')
    reference = fields.Reference(
        selection='_select_models', compute='_compute_product_cost')

    def _select_models(self):
        models = self.env['ir.model'].search(
            [('model', 'in', self._get_models())])
        return [(x['model'], x['name']) for x in models] + [('', '')]

    @api.multi
    @api.depends('product_id',)
    def _compute_product_cost(self):
        po_l_obj = self.env['purchase.order.line']
        product_ids = [x.product_id.id for x in self]
        if not product_ids or not product_ids[0]:
            # product_ids == [False] for first created line
            return
        invoices = self._get_invoice_data(product_ids)
        for invent_line in self:
            if not invent_line.inventory_id or \
                    not invent_line.product_id or \
                    invent_line.inventory_id.state not in ('done'):
                continue
            # get cost from supplier invoice
            explanation = ''
            cost_price = 0
            reference = False
            if invoices:
                cost_price = invoices[invent_line.product_id.id].get(
                    'price_unit')
                explanation = _('Supplier Invoice')
                if invoices[invent_line.product_id.id].get('id'):
                    reference = 'account.invoice,%s' % invoices[
                        invent_line.product_id.id].get('id')
            if not cost_price:
                # get cost price from purchase
                po_line = po_l_obj.search(
                    [('product_id', '=', invent_line.product_id.id),
                     ('order_id.state', '=', 'done')
                     ], limit=1)
                if po_line:
                    cost_price = po_line.price_unit
                    explanation = _('Purchase')
                    reference = 'purchase.order,%s' % po_line.order_id.id
            if not cost_price:
                # get cost price from supplier info
                sup_info = invent_line.product_id.seller_ids
                if sup_info and sup_info[0].pricelist_ids:
                    cost_price = sup_info[0].pricelist_ids[0].price
                    explanation = _('Supplier info')
                    reference = 'product.supplierinfo,%s' % sup_info[0].id
            if not cost_price:
                # get cost price from supplier info
                sup_info = invent_line.product_id.seller_id
                if invent_line.product_id.standard_price:
                    cost_price = invent_line.product_id.standard_price
                    explanation = _('Cost from product "%s" standard_price') %\
                        invent_line.product_id.default_code or\
                        invent_line.product_id.name
            if not cost_price:
                explanation = _('Not Cost found')
                reference = ''
            invent_line.calc_product_cost = cost_price
            invent_line.cost_origin = explanation
            if reference:
                invent_line.reference = reference

    @api.multi
    @api.depends('calc_product_cost', 'manual_product_cost')
    def _compute_value(self):
        for line in self:
            if line.manual_product_cost:
                line.value = line.manual_product_cost * line.product_qty
            else:
                line.value = line.calc_product_cost * line.product_qty

    @api.model
    def _get_invoice_data(self, product_ids):
        invoices = defaultdict(dict)
        query = """ SELECT l.product_id, max(l.create_date) AS date
            FROM account_invoice_line l
                LEFT JOIN account_invoice i ON i.id = l.invoice_id
            WHERE l.product_id IN %s
              AND i.type = 'out_invoice' AND i.state in ('open', 'paid')
            GROUP BY 1
            ORDER BY date ASC
            LIMIT 1
        """
        self.env.cr.execute(query, (tuple(product_ids),))
        oldier = self.env.cr.fetchall()
        if oldier:
            query = """ SELECT l.product_id, l.price_unit, i.id, i.number
                FROM account_invoice_line l
                    LEFT JOIN account_invoice i ON i.id = l.invoice_id
                WHERE l.product_id IN %s AND l.create_date >= %s
                    AND i.type = 'out_invoice' AND i.state in ('open', 'paid')
                ORDER BY l.create_date ASC
            """
            self.env.cr.execute(query, (tuple(product_ids), oldier[0][1]))
            res = self.env.cr.fetchall()
            invoices = defaultdict(dict)
            for elm in res:
                invoices[elm[0]].update(
                    {'price_unit': elm[1], 'id': elm[2], 'number': elm[3]})
        return invoices

    def _get_models(self):
        return [
            'account.invoice',
            'purchase.order',
            'product.supplierinfo',
            'product.product',
        ]

    @api.multi
    def button_info_origin(self):
        self.ensure_one()
        if self.reference:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': self.reference._model._name,
                'res_id': self.reference.id,
                'target': 'new',
                'name': _("%s: %s: '%s'" % (
                    self.reference._model._description,
                    self.product_id.display_name, self.value)),
            }
        return False
