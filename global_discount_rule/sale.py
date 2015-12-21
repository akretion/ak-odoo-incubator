# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from collections import defaultdict


def utf8(data):
    return data.encode('utf-8')


def sum_in_dict(data, first_key, mapping):
    if data.get(first_key):
        for key, value in mapping.items():
            data[first_key][key] += value
    else:
        data[first_key].update(mapping)
    return data


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    explanation = fields.Text()

    @api.multi
    def apply_global_discount(self):
        '''
        - matching product rules:
            - product list: id, product_tmpl_id, categ_id, defaut_code
        '''
        for sale in self:
            trace = []
            # candidates_conditions = {}
            self.remove_old_promotion()
            products, tmpls, categs, sequence = self.get_infos_from_sale()
            global_rules = sale.get_relevant_rules_from_partner()
            product_ids = products.keys()
            for rule in global_rules:
                initial_domain = [('product_id', 'in', product_ids)]
                initial_domain.append(('global_discount_id', '=', rule.id))
                domain = rule.get_domain()
                match_products = self.env['product.price.domain'].search(
                    domain + initial_domain)
                print 'match', match_products
                if match_products:
                    candidate = sale.compute_candidate_rule(
                        products, match_products, rule, trace)
            for product_id in products:
                domain = [('product_id', '=', product_id),
                          ('global_discount_id', 'in',
                           [x.id for x in global_rules])]
                match = self.env['product.price.domain'].search(domain)
                match_rules = list(set([x.global_discount_id for x in match]))
                products[product_id]['condition'] = sale.get_best_rule4product(
                    match_rules, products[product_id])
                sale.update_sale_product_lines(
                    products[product_id], product_id)
            # import pdb; pdb.set_trace()
            trace.append(str(products).replace('}', '\n}'))
            # sale.update_sale_lines(products, conds, trace)
            # sale.update_sale_lines(products, conditions, trace)
            if trace:
                vals = {'explanation': trace}
            else:
                vals = {'explanation': False}
            sale.write(vals)

    @api.model
    def update_sale_product_lines(self, product, product_id):
        if product.get('condition'):
        # if product.get('condition') and len(product['conditions']) == 1:
            condition = product['condition']
            vals = {
                'global_discount_id': condition['global_discount_id'],
                'discount': product['condition']['value'],
                'threshold': "qty %s" % condition['threshold'],
            }
            sale_lines = self.env['sale.order.line'].search(
                [('product_id', '=', product_id)])
            sale_lines.write(vals)

    @api.multi
    def get_best_rule4product(self, rules, product):
        self.ensure_one()
        conditions = {}
        for rule in rules:
            condition = self.get_best_condition(rule, product)
            if condition:
                conditions.update({rule.id: condition})
        if conditions:
            print conditions
            condition_values = {
                cond['value']: id for id, cond in conditions.items()}
            max_discount = max([x for x in condition_values])
            best_condition = condition_values[max_discount]
            return conditions[best_condition]
        return False

    @api.multi
    def get_best_condition(self, rule, product):
        condition = {}
        self.ensure_one()
        for disc in rule.discount_rule_ids:
            if product['qty'] >= disc.qty:
                condition = {
                    'id': disc.id,
                    'global_discount_id': disc.global_discount_id.id,
                    'type': 'percent',
                    'value': disc.discount,
                    'threshold': disc.qty,
                }
        return condition

    @api.model
    def update_sale_lines(self, products, conditions, trace):
        print products
        for key, params in products.items():
            rules = params['rules']
            if len(params['rules']) == 1:
                rule = params['rules'][0]
                sale_lines = self.env['sale.order.line'].search(
                    [('product_id', '=', key)])
                vals = {'discount_rule_id': rule.id}
                if conditions.get(rule.id):
                    vals['discount'] = conditions[rule.id]['value']
                    vals['threshold'] = (_("qty: %s")
                                         % conditions[rule.id]['threshold'])
                sale_lines.write(vals)
            else:
                rule_names = [utf8(x.name) for x in rules]
                mess = 'Multiple conditions:'
                mess += "prd %s, regles %s" % (params['name'], rule_names)
                trace.append(mess)
        return trace

    @api.multi
    def compute_candidate_rule(
            self, products, match_products, rule, trace):
        self.ensure_one()
        match = False
        condition = {}
        qty_total = sum([products[x.product_id.id]['qty']
                         for x in match_products])
        # amount = sum([products[x.product_id.id]['amount']
        #               for x in match_products])
        # names = [utf8(x.product_id.display_name)
        #          for x in match_products]
        # print names
        # qty_by_product = {x.product_id: False for x in match_products}
        # azerty = defaultdict(dict)
        for disc in rule.discount_rule_ids:
            if qty_total >= disc.qty:
                # condition = {'type': 'percent',
                #              'value': disc.discount,
                #              'threshold': disc.qty}
                match = True
        if match:
            for domain in match_products:
                products[domain.product_id.id]['conditions'].append(rule)
        return True

    @api.multi
    def get_infos_from_sale(self):
        self.ensure_one()
        products = defaultdict(dict)
        tmpl_products = defaultdict(dict)
        categs = defaultdict(dict)
        for line in self.order_line:
            mapping = {'qty': line.product_uom_qty,
                       'amount': line.price_subtotal,
                       'name': line.product_id.display_name,
                       'conditions': []}
            products = sum_in_dict(
                products, line.product_id.id, mapping)
            tmpl_products = sum_in_dict(
                tmpl_products, line.product_id.product_tmpl_id.id,
                mapping)
            categs = sum_in_dict(
                categs, line.product_id.categ_id.id, mapping)
        return (products, tmpl_products, categs, line.sequence + 1)

    @api.multi
    def get_relevant_rules_from_partner(self):
        self.ensure_one()
        common_rules = self.env['global.discount.rule'].search(
            [('partner_rule_ids', '=', False)])
        excluded_rules = self.env['global.discount.rule'].browse(False)
        partner = self.partner_id
        if self.partner_id.parent_id:
            partner = self.partner_id.parent_id
        partner_rules = self.env['partner.price.domain'].search(
            [('partner_id', '=', partner.id)])
        for rule in partner_rules:
            excluded_rules |= rule.global_discount_id
        query = """SELECT global_discount_id FROM partner_price_domain
                WHERE active = 'f'
                   AND '%s' LIKE ref""" % partner.ref
        self._cr.execute(query)
        excluded_rules |= self.env['global.discount.rule'].browse(
            [x[0] for x in self._cr.fetchall()])
        return common_rules - excluded_rules

    @api.multi
    def remove_old_promotion(self):
        self.ensure_one()
        # disc_product = self.env.ref(
        #     'global_discount_rule.discount_product_from_rule').id
        # disc_lines = self.order_line.search([
        #     ('order_id', '=', self.id), ('product_id', '=', disc_product)])
        # disc_lines.unlink()
        disc_lines = self.order_line.search([
            ('order_id', '=', self.id),
            '|',
            ('threshold', '!=', False),
            ('global_discount_id', '!=', False)])
        vals = {'global_discount_id': False,
                'threshold': False, 'discount': False}
        disc_lines.write(vals)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    global_discount_id = fields.Many2one(
        comodel_name='global.discount.rule', string="Discount Rule",
        copy=False,
        help="")
    threshold = fields.Char(help="Over this value, give a promotion")
