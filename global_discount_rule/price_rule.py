# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class GlobalDiscountRule(models.Model):
    _name = 'global.discount.rule'
    _description = "Global Discount Rule"

    name = fields.Char(required=True)
    based = fields.Selection(selection=[
        ('quantity', 'Quantity'),
        ('amount', 'Amount'),
        ],
        default='quantity',
        help="")
    display_name = fields.Char(compute='_compute_display_name')
    start_date = fields.Date(
        string='Start date',
        help="")
    end_date = fields.Date(
        string='End date',
        help="")
    product_id = fields.Many2one(
        'product.product', string="Product", required=True,
        domain=[('type', '=', 'service')],
        help="Product used to display the global discount in the sale order.")
    display_partner = fields.Boolean(
        string='Display customer',
        help="Display customer block to exclude some of them of this rule")
    short_name = fields.Char(string='Short Name')
    discount_rule_ids = fields.One2many(
        comodel_name='discount.rule', inverse_name='global_discount_id')
    product_rule_ids = fields.One2many(
        comodel_name='product.price.domain', inverse_name='global_discount_id')
    partner_rule_ids = fields.One2many(
        comodel_name='partner.price.domain', inverse_name='global_discount_id')
    sequence = fields.Integer()
    active = fields.Boolean(default=True)

    @api.one
    @api.constrains('end_date', 'start_date')
    def _check_tax_categ(self):
        if self.end_date and self.start_date:
            if self.end_date <= self.start_date:
                raise ValidationError(
                    _("'End Date' field must be upper than 'Start Date'"))

    @api.one
    @api.constrains('display_partner')
    def _check_partner(self):
        if not self.display_partner and self.partner_rule_ids:
            raise ValidationError(
                _("'Excluded Customers' must be displayed if not empty.\n"
                  "Check '%s' field."
                  % self._fields['display_partner'].string))

    @api.multi
    @api.depends('name', 'short_name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.short_name or record.name

    @api.multi
    def get_domain(self):
        self.ensure_one()
        domain = []
        for line in self.product_rule_ids:
            domain_line = []
            columns = ['categ_id', 'product_tmpl_id',
                       'product_id', 'default_code']
            columns = ['product_id']
            for field in columns:
                if line[field]:
                    value = line[field]
                    if field[-2:] == 'id':
                        value = line[field].id
                    if domain_line:
                        domain_line.insert(0, '&')
                    domain_line.append((field, '=', value))
            if domain:
                domain.insert(0, '|')
            domain.extend(domain_line)
        return domain

    @api.model
    def default_get(self, fields_list):
        vals = super(GlobalDiscountRule, self).default_get(fields_list)
        if self.env.ref('global_discount_rule.discount_product_from_rule'):
            vals['product_id'] = self.env.ref(
                'global_discount_rule.discount_product_from_rule').id
        return vals

    @api.multi
    def write(self, vals):
        ''' We need to activate/deactivate all depending record
            according to model
        '''
        res = super(GlobalDiscountRule, self).write(vals)
        models = ['discount.rule', 'product.price.domain',
                  'partner.price.domain']
        for record in self:
            if 'active' in vals:
                for model in models:
                    states_to_write = self.env[model].search(
                        [('global_discount_id', '=', record.id),
                         # True becomes False and False becomes True
                         ('active', '=', not vals['active'])])
                    states_to_write.write({'active': vals['active']})
            if 'start_date' in vals or 'end_date' in vals:
                record.run_discount_rule_state()
        return res

    @api.multi
    def unlink(self):
        # TODO also delete all children: cascade
        super(GlobalDiscountRule, self).unlink()

    @api.model
    def run_discount_rule_state(self):
        """ Update activation according to dates fields
            propagate to o2m
            TODO complete
        """
        disc_rules = self.env['global.discount.rule'].search(
            ['|', '&',
             ('start_date', '=', False),
             ('end_date', '=', False),
             '|', '&',
             ('start_date', '<=', fields.Date.today()),
             ('end_date', '=', False),
             '|', '&',
             ('start_date', '<=', False),
             ('end_date', '>=', fields.Date.today()),
             ('start_date', '<=', fields.Date.today()),
             ('end_date', '>=', fields.Date.today()),
             ('active', '=', False)])
        if disc_rules:
            disc_rules.write({'active': True})
        disc_rules = self.env['global.discount.rule'].search(
            ['|', '|',
             ('start_date', '>=', fields.Date.today()),
             ('end_date', '<=', fields.Date.today()),
             ('start_date', '>=', fields.Date.today()),
             ('end_date', '<=', fields.Date.today()),
             ('active', '=', True)])
        if disc_rules:
            disc_rules.write({'active': False})
        return True


class DiscountRule(models.Model):
    _name = 'discount.rule'
    _description = "Discount Rule"
    _order = 'qty'

    name = fields.Char()
    qty = fields.Integer(string='Qty')
    discount = fields.Float()
    global_discount_id = fields.Many2one(
        comodel_name='global.discount.rule', string='Global Discount Rule',
        help="")
    active = fields.Boolean(default=True)
    sequence = fields.Integer()


class ProductPriceDomain(models.Model):
    _name = 'product.price.domain'
    _description = "Product Price Domain"

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template', string='Product template',
        help="")
    product_id = fields.Many2one(
        comodel_name='product.product', string="Product",
        help="")
    default_code = fields.Char(
        string='Reference', help="Product code")
    categ_id = fields.Many2one(
        comodel_name='product.category', string='Category',
        help="")
    global_discount_id = fields.Many2one(
        comodel_name='global.discount.rule', string='Global Discount Rule',
        required=True, readonly=True,
        help="")
    active = fields.Boolean(default=True)
    sequence = fields.Integer()

    @api.one
    @api.constrains('product_tmpl_id', 'product_id', 'categ_id')
    def _check_product_rule(self):
        fields = ['product_tmpl_id', 'product_id', 'categ_id']
        if len([x for x in fields if bool(self[x])]) > 1:
            field_names = [self._fields[x].string for x in fields]
            raise ValidationError(
                _("We must have only one of these fields '%s'\n"
                  "per each Product lines." % field_names))


class PartnerPriceDomain(models.Model):
    _name = 'partner.price.domain'
    _description = "Partner Price Domain"

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner',
        help="")
    ref = fields.Char(help="Partner code")
    global_discount_id = fields.Many2one(
        comodel_name='global.discount.rule', string='Global Discount Rule',
        required=True, readonly=True,
        help="")
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
