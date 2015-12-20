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

    discount_rule_ids = fields.Many2many(
        comodel_name='global.discount.rule')

    @api.multi
    def apply_global_discount(self):
        '''
        - matching product rules:
            - product list: id, product_tmpl_id, categ_id, defaut_code
        '''
        for sale in self:
            trace = []
            conditions = {}
            self.remove_old_promotion()
            products, tmpls, categs, sequence = self.get_infos_from_sale()
            discount_rules = sale.get_relevant_rules_from_partner()
            product_ids = products.keys()
            # print products
            for rule in discount_rules:
                initial_domain = [('product_id', 'in', product_ids)]
                initial_domain.append(('global_discount_id', '=', rule.id))
                domain = rule.get_domain()
                match_prds_domain = self.env['product.price.domain'].search(
                    domain + initial_domain)
                print 'match', match_prds_domain
                if match_prds_domain:
                    conditions.update(sale.compute_candidate_rule(
                        products, match_prds_domain, rule, trace))
            sale.update_sale_line(products, conditions, trace)
            if trace:
                vals = {'note': '\n'.join(trace)}
            else:
                vals = {'note': False}
            sale.write(vals)

    @api.multi
    def compute_candidate_rule(
            self, products, match_prds_domain, rule, trace):
        self.ensure_one()
        match = False
        condition = {}
        qty = sum([products[x.product_id.id]['qty']
                   for x in match_prds_domain])
        amount = sum([products[x.product_id.id]['amount']
                      for x in match_prds_domain])
        names = [utf8(x.product_id.display_name)
                 for x in match_prds_domain]
        print names
        for disc in rule.discount_rule_ids:
            if qty >= disc.qty:
                condition = {'type': 'percent',
                             'value': disc.discount,
                             'threshold': disc.qty}
                match = True
        if match:
            for domain in match_prds_domain:
                products[domain.product_id.id]['rules'].append(rule)
        return {rule.id: condition}

    @api.model
    def update_sale_line(self, products, conditions, trace):
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
    def get_infos_from_sale(self):
        self.ensure_one()
        products = defaultdict(dict)
        tmpl_products = defaultdict(dict)
        categs = defaultdict(dict)
        for line in self.order_line:
            mapping = {'qty': line.product_uom_qty,
                       'amount': line.price_subtotal,
                       'name': line.product_id.display_name,
                       'rules': []}
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
        # print 'comm, exclu, final', common_rules, excluded_rules, common_rules - excluded_rules, '   ---'
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
            ('discount_rule_id', '!=', False)])
        disc_lines.write({'discount_rule_id': False, 'threshold': False})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount_rule_id = fields.Many2one(
        comodel_name='global.discount.rule', string="Discount Rule",
        copy=False,
        help="")
    threshold = fields.Char(help="Over this value, give a promotion")
