# coding: utf-8
# © 2015 Akretion, Valentin CHEMIERE <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    base_price_unit = fields.Float(string='Base Price Unit')
    pricelist_id = fields.Many2one(
        related="order_id.pricelist_id", readonly=True)
    option_ids = fields.One2many(
        comodel_name='sale.order.line.option',
        inverse_name='sale_line_id', string='Options', copy=True)

    def product_id_change(self, cr, uid, ids, pricelist, product,
                          qty=0,
                          uom=False,
                          qty_uos=0,
                          uos=False,
                          name='',
                          partner_id=False,
                          lang=False,
                          update_tax=True,
                          date_order=False,
                          packaging=False,
                          fiscal_position=False,
                          flag=False,
                          context=None):
        res = super(SaleOrderLine, self).product_id_change(
            cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name,
            partner_id, lang, update_tax, date_order, packaging,
            fiscal_position, flag, context)
        if product:
            res['value']['base_price_unit'] = res['value']['price_unit']
            res['value']['option_ids'] = self._set_option_lines(
                cr, uid, product, context=context)
        return res

    @api.model
    def _set_option_lines(self, product_id):
        lines = []
        bom_lines = self.env['mrp.bom.line'].with_context(
            filter_bom_with_product_id=product_id).search([])
        for bline in bom_lines:
            if bline.default_qty:
                # TODO refactor v10 with update_sale_line_option() below
                vals = {'bom_line_id': bline.id,
                        'product_id': bline.product_id.id,
                        'qty': bline.default_qty}
                lines.append((0, 0, vals))  # create
        if lines:
            return lines

    @api.multi
    def _onchange_eval(self, field_name, onchange, result):
        super(SaleOrderLine, self)._onchange_eval(field_name, onchange, result)
        # As onchange is an old api version we have to hack to update
        # the price unit with the option value
        if 'product_id_change' in onchange:
            self._onchange_option()

        # For some strange reason changing the qty of the product in the
        # option will not recompute the price unit
        # in order to be sure to recompute the price for it here
        if field_name == 'option_ids':
            self._onchange_option()

    @api.onchange(
        'option_ids',
        'base_price_unit')
    def _onchange_option(self):
        final_options_price = 0
        for option in self.option_ids:
            final_options_price += option.line_price
            self.price_unit = final_options_price + self.base_price_unit


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _prepare_vals_lot_number(self, order_line, index_lot):
        res = super(SaleOrder, self)._prepare_vals_lot_number(
            order_line, index_lot)
        res['option_ids'] = [
            (6, 0, [line.id for line in order_line.option_ids])
        ]
        return res


class SaleOrderLineOption(models.Model):
    _name = 'sale.order.line.option'

    @api.model
    def default_get(self, fields):
        res = super(SaleOrderLineOption, self).default_get(fields)
        sale_line_id = self.env.context.get('active_id')
        if sale_line_id:
            sale_line = self.env['sale.order.line'].browse(sale_line_id)
            if sale_line.product_id:
                product_id = sale_line.product_id.id
                bom_lines = self.env['mrp.bom.line'].with_context(
                    filter_bom_with_product_id=product_id).search([])
                res['product_ids'] = [x.product_id.id for x in bom_lines]
        return res

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line',
        required=True,
        ondelete='cascade')
    bom_line_id = fields.Many2one(
        comodel_name='mrp.bom.line', string='Bom Line')
    product_ids = fields.Many2many(
        comodel_name='product.product', compute='_compute_opt_products')
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    qty = fields.Integer(default=1)
    line_price = fields.Float(compute='_compute_price', store=True)

    @api.multi
    def _compute_opt_products(self):
        prd_ids = [x.product_id.id
                   for x in self[0].bom_line_id.bom_id.bom_line_ids]
        for rec in self:
            rec.product_ids = prd_ids

    @api.multi
    def _get_bom_line_price(self):
        self.ensure_one()
        pricelist = self.sale_line_id.pricelist_id.with_context({
            'uom': self.bom_line_id.product_uom.id,
            'date': self.sale_line_id.order_id.date_order,
        })
        price = pricelist.price_get(
            self.bom_line_id.product_id.id,
            self.bom_line_id.product_qty or 1.0,
            self.sale_line_id.order_id.partner_id.id)
        return price[pricelist.id] * self.bom_line_id.product_qty * self.qty

    @api.multi
    @api.depends('qty')
    def _compute_price(self):
        for record in self:
            if record.bom_line_id and record.sale_line_id.pricelist_id:
                record.line_price = record._get_bom_line_price()
            else:
                record.line_price = 0
