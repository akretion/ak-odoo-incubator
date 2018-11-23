# coding: utf-8
# © 2018 Mourad El Hadj Mimoun @ Akretion
# © 2018 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, models, fields, _
import odoo.addons.decimal_precision as dp


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    to_recompute = fields.Boolean()

    @api.one
    def button_compute_cost(self):
        "Compute or reset"
        self.write({'to_recompute': not self.to_recompute})


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    calc_product_cost = fields.Float(
        compute='_compute_product_cost', string='Computed cost', store=True,
        digits=dp.get_precision('Account'))
    manual_product_cost = fields.Float(
        string='Manual cost',
        digits=dp.get_precision('Account'))
    value = fields.Float(
        compute='_compute_value', string='Value', store=True,
        digits=dp.get_precision('Account'))
    cost_origin = fields.Text(
        compute='_compute_product_cost', store=True,
        help='Explain computation method for each product')
    reference = fields.Reference(
        selection='_select_models', compute='_compute_product_cost',
        store=True)

    def _select_models(self):
        models = self.env['ir.model'].search(
            [('model', 'in', self._get_models())])
        return [(x['model'], x['name']) for x in models] + [('', '')]

    @api.multi
    @api.depends('product_id', 'product_qty', 'manual_product_cost',
                 'inventory_id.state', 'inventory_id.to_recompute')
    def _compute_product_cost(self):
        custom_data_source = self._get_custom_data_source()
        po_l_obj = self.env['purchase.order.line']
        product_ids = [x.product_id.id for x in self]
        # product_ids == [False] for first created line
        if not product_ids or not product_ids[0]:
            return
        invoices = self._get_invoice_data(
            product_ids, company=self.env.user.company_id)
        for line in self:
            if line.inventory_id.state not in ('done') and \
                    not line.inventory_id.to_recompute:
                line.cost_origin = _("Click on 'Compute cost'")
                continue
            if not line.inventory_id or not line.product_id:
                continue
            # get cost from supplier invoice
            explanation = ''
            cost_price = 0
            reference = False
            if not cost_price:
                if custom_data_source:
                    cost_price = self._get_custom_cost(custom_data_source)
                # get cost price from supplier info
                sup_info = line.product_id.seller_ids
                if sup_info and sup_info[0].price:
                    cost_price = sup_info[0].price
                    explanation = _('Supplier info')
                    reference = 'product.supplierinfo,%s' % sup_info[0].id
            if not cost_price and invoices:
                cost_price = invoices[line.product_id.id].get(
                    'price_unit')
                explanation = _('Supplier Invoice')
                if invoices[line.product_id.id].get('id'):
                    reference = 'account.invoice,%s' % invoices[
                        line.product_id.id].get('id')
            if not cost_price:
                # get cost price from purchase
                po_line = po_l_obj.search(
                    [('product_id', '=', line.product_id.id),
                     ('order_id.state', '=', 'done')
                     ], limit=1)
                if po_line:
                    cost_price = po_line.price_unit
                    explanation = _('Purchase')
                    reference = 'purchase.order,%s' % po_line.order_id.id
            if not cost_price:
                # get cost price from supplier info
                sup_info = line.product_id.seller_id
                if line.product_id.standard_price_:
                    cost_price = line.product_id.standard_price_
                    explanation = _('Product standard_price')
                    reference = 'product.product,%s' % line.product_id.id
            if not cost_price:
                explanation = _('No Cost found')
                reference = ''
            line.calc_product_cost = cost_price
            line.cost_origin = explanation
            if reference:
                line.reference = reference

    def _get_custom_data_source(self):
        return None

    def _get_custom_cost(self, custom_data_source):
        return None

    @api.multi
    @api.depends('calc_product_cost', 'manual_product_cost')
    def _compute_value(self):
        for line in self:
            if line.manual_product_cost:
                line.value = line.manual_product_cost * line.product_qty
            else:
                line.value = line.calc_product_cost * line.product_qty

    @api.model
    def _get_invoice_data(self, product_ids, company):
        invoices = defaultdict(dict)
        query = """ SELECT l.product_id, max(l.create_date) AS date
            FROM account_invoice_line l
                LEFT JOIN account_invoice i ON i.id = l.invoice_id
            WHERE l.product_id IN %s AND i.company_id = %s
              AND i.type = 'in_invoice' AND i.state in ('open', 'paid')
            GROUP BY 1
            ORDER BY date ASC
            LIMIT 1
        """
        self.env.cr.execute(query, (tuple(product_ids), company.id))
        oldier = self.env.cr.fetchall()
        if oldier:
            query = """ SELECT l.product_id, l.price_unit, i.id, i.number
                FROM account_invoice_line l
                    LEFT JOIN account_invoice i ON i.id = l.invoice_id
                WHERE l.product_id IN %s AND i.company_id = %s
                    AND l.create_date >= %s
                    AND i.type = 'in_invoice' AND i.state in ('open', 'paid')
                ORDER BY l.create_date ASC
            """
            self.env.cr.execute(query, (
                tuple(product_ids), company.id, oldier[0][1]))
            res = self.env.cr.fetchall()
            invoices = defaultdict(dict)
            for elm in res:
                invoices[elm[0]].update(
                    {'price_unit': elm[1], 'id': elm[2], 'number': elm[3]})
        return invoices

    @api.model
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
