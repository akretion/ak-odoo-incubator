# coding: utf-8
# © 2016 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp


class PricelistGenerator(models.Model):
    _name = "pricelist.item.generator"

    sequence = fields.Integer(string='Sequence', default=5)
    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(
        string='Active', default=False,
        help="if checked, rules are exported towards "
             "'Product pricelist items'")
    to_update = fields.Boolean(
        string='To update', readonly=True, default=True,
        help="Flag if the pricelist items needs to be build")
    price_version_id = fields.Many2one(
        comodel_name='product.pricelist.version',
        string='Pricelist version', required=True,
        domain="[('pricelist_id.type', '=', 'sale')]",
        help="Only pricelist of 'Sale' type")
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company',
        related='price_version_id.company_id',
        readonly=True, store=True)
    trace = fields.Char(
        string='Last update', readonly=True,
        help="Describe what modifications where happened on "
             "'Pricelist Items' the last time you valid "
             "modifications (click on 'Build pricelist' button)'")
    already_used = fields.Boolean('Already used')
    product_condition_ids = fields.One2many(
        'pricelist.product.condition',
        'price_generator_id',
        string='Product conditions',
        help="In which products are applied the price elements")
    item_template_ids = fields.One2many(
        'pricelist.item.template',
        'price_generator_id',
        string='Pricelist item templates',
        help="Pricelist item template")

    @api.multi
    def write(self, vals):
        if 'sequence' in vals or 'name' in vals:
            vals['to_update'] = True
        return super(PricelistGenerator, self).write(vals)

    @api.model
    def run_generate_pricelist_item(self):
        "Method launch by cron"
        return self.search([]).build_pricelist_item()

    @api.multi
    def build_pricelist_item(self):
        for gen in self:
            item_tpls = {}
            hashkeys = {}
            products = gen.get_products_from_condition()
            for item_tpl in gen.item_template_ids:
                # sequence is compose of two parts
                self.env['pricelist.item.template']._set_tpl_sequence(
                    gen.sequence, item_tpl.sequence)
                # see _get_hashkey() for explanation
                hashkeys[item_tpl.id] = gen._get_hashkey(item_tpl)
                # get datas for write purpose
                item_tpls[item_tpl.id] = gen._prepare_item_vals(item_tpl)
            if products:
                products = self.product_filter(products)
                # synchronization with 'product.pricelist.item'
                actions_count = gen._update_product_pricel_items(
                    item_tpls, products, hashkeys)
            else:
                actions_count = {}
                # delete all pricelist.item
                actions_count['deleted'] = (
                    gen._unlink_product_pricel_items(item_tpls, products))
            gen.write({'to_update': False})
            # traceability of changes
            trace = self._set_traceability(actions_count)
            self.write({'trace': trace})
        return True

    @api.multi
    def get_products_from_condition(self):
        self.ensure_one()
        products = []
        # loop on condition to get products
        for condition in self.product_condition_ids:
            products.extend(condition._get_products_from_condition())
            products = list(set(products))
        return products

    @api.model
    def product_filter(self, products):
        "You may inherit this method to filter this list"
        return products

    @api.multi
    def _get_hashkey(self, item_tpl):
        """ haskey avoids to trigger synchro if datas are the same
            example : price rule is the same but you add a product:
            you don't want rewrite existing rules with no changes
            (avoid needless synchro with external applications)
        """
        self.ensure_one()
        keys = ''
        for field in item_tpl._columns:
            if item_tpl._columns[field]._type == 'many2one':
                keys += unicode(item_tpl[field].id)
            else:
                keys += unicode(item_tpl[field])
        keys += unicode(self.name)
        keys += unicode(self.company_id.id)
        keys += unicode(self.price_version_id.id)
        # TOFIX
        keys += unicode(item_tpl._tpl_sequence)
        return keys

    @api.multi
    def _prepare_item_vals(self, item_tpl):
        self.ensure_one()
        return {
            'auto': True,
            'min_quantity': item_tpl.min_quantity,
            'base': item_tpl.base,
            'item_template_id': item_tpl.id,
            'price_discount': item_tpl.price_discount,
            'price_surcharge': item_tpl.price_surcharge,
            # 'sequence': item_tpl.tpl_sequence,
            'price_round': item_tpl.price_round,
            # TODO ROADMAP : allow price_version change with deletions
            'price_version_id': self.price_version_id.id,
            'name': self.name,
            'price_generator_id': self.id,
            'company_id': self.company_id.id,
        }

    @api.multi
    def _update_product_pricel_items(self, item_tpls_dict, products, hashkeys):
        self.ensure_one()
        item_m = self.env['product.pricelist.item']
        item_tpl_ids = item_m.search([('price_generator_id', '=', self.id)])
        price_items = item_tpl_ids.read(
            ['hashkey', 'item_template_id', 'product_id'])
        # print '\nitem_tpls_dict', item_tpls_dict, '\nitem_tpl_ids', item_tpl_ids, '\nprice_items', price_items
        price_item_infos = {}
        for item in price_items:
            item_key = "%s - %s" % (item['product_id'][0],
                                    item['item_template_id'][0])
            price_item_infos[item_key] = {
                'id': item['id'],
                'hashkey': item['hashkey'],
            }
        actions_count = {
            'created': 0,
            'modified': 0,
            'untouched': 0,
            'deleted': 0,
        }
        actions_count['deleted'] = self._unlink_product_pricel_items(
            item_tpls_dict, products)
        for item_template_id, tpl in item_tpls_dict.items():
            for product in products:
                item_key = "%s - %s" % (product.id, item_template_id)
                price_item_vals = tpl.copy()
                hashkey = hashkeys[item_template_id]
                price_item_vals.update({
                    'product_id': product.id,
                    'hashkey': hashkey,
                })
                if item_key in price_item_infos.keys():
                    if hashkey != price_item_infos[item_key].get('hashkey'):
                        actions_count['modified'] += 1
                        item_m.write(
                            [price_item_infos[item_key]['id']],
                            price_item_vals)
                    else:
                        actions_count['untouched'] += 1
                else:
                    actions_count['created'] += 1
                    item_m.create(price_item_vals)
        return actions_count

    @api.multi
    def activate_generator(self):
        for generator in self:
            if generator.active is False:
                vals = {'active': True, 'to_update': True,
                        'already_used': True}
            else:
                vals = {'active': False}
                items = self.env['pricelist.item.template'].search(
                    [('price_generator_id', '=', generator.id)])
                products = generator.get_products_from_condition()
                deleted = len(items) * len(products)
                generator._unlink_product_pricel_items()
                trace = self._set_traceability({'deleted': deleted})
                vals.update({'trace': trace})
            generator.write(vals)
            return True

    @api.multi
    def _unlink_product_pricel_items(self, item_tpls=None, products=None):
        self.ensure_one()
        domain = []
        if products:
            product_ids = [x.id for x in products]
            domain.extend(['|', ('product_id', 'not in', product_ids)])
        if item_tpls:
            domain.extend([('item_template_id', 'not in', item_tpls.keys())])
        if not products or not item_tpls:
            domain = []
        domain.extend([('price_generator_id', '=', self.id)])
        items_to_unlink = self.env['product.pricelist.item'].search(domain)
        if items_to_unlink:
            items_to_unlink.unlink()
        return len(items_to_unlink)

    @api.model
    def _set_traceability(self, actions_count):
        types = {
            'created': _('created'),
            'modified': _('modified'),
            'untouched': _('untouched'),
            'deleted': _('deleted')}
        traces = []
        for key in actions_count:
            if actions_count[key] > 0:
                traces.append(unicode(actions_count[key]) + ' ' + types[key])
        return ', '.join(traces)


class PricelistProductCondition(models.Model):
    _name = "pricelist.product.condition"
    _description = "Products selection by criterias"

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product Variant',
        help="If product is selected, no other criterias can be take account")
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Product',
        help="If product is selected, no other criterias can be take account")
    categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Category',
        help="Products of the category or products of children categories")
    price_generator_id = fields.Many2one(
        comodel_name='pricelist.item.generator',
        string='Generator',
        required=True)

    @api.multi
    def unlink(self):
        self[0].price_generator_id.write({'to_update': True})
        return super(PricelistProductCondition, self).unlink()

    @api.model
    def create(self, vals):
        self.env['pricelist.item.generator'].search(
            [('id', '=', vals['price_generator_id'])]).write(
            {'to_update': True})
        return super(PricelistProductCondition, self).create(vals)

    @api.multi
    def write(self, vals):
        self.price_generator_id.write({'to_update': True})
        return super(PricelistProductCondition, self).write(vals)

    @api.multi
    def _get_products_from_condition(self):
        self.ensure_one()
        if self.product_id:
            return [self.product_id]
        return self.env['product.product'].search(
            self._get_domain_for_condition())

    @api.multi
    def _get_domain_for_condition(self):
        self.ensure_one()
        if self.product_tmpl_id:
            return [('product_tmpl_id', '=', self.product_tmpl_id.id)]
        if self.categ_id:
            return [('categ_id.parent_id', 'child_of', self.categ_id.id)]


class AbstractPriceListItemGenerator(models.AbstractModel):
    _name = "abstract.pricelist.item.generator"
    _description = "Abstract Pricelist Items Generator"

    price_generator_id = fields.Many2one(
        comodel_name='pricelist.item.generator',
        string='Generator', readonly=True)
    min_quantity = fields.Integer(default=1)

    @api.one
    @api.constrains('price_discount', 'price_surcharge')
    def _check_price_elements(self):
        # check price validity
        if self.price_discount == 0 and self.price_surcharge == 0:
            raise UserError(
                    _("'Discount' or 'Surcharge' must be different of 0."))


ITEM_FIELDS = ['sequence', 'base', 'price_surcharge', 'price_discount',
               'price_round', 'price_min_margin', 'price_max_margin']


class PricelistItemTemplateBase(models.Model):
    _name = 'pricelist.item.template'
    _description = "Pricelist item template"

    _order = "sequence, min_quantity desc"
    _tpl_sequence = ''

    def __init__(self, registry, cr):
        # TODO get fields
        return super(PricelistItemTemplateBase, self).__init__(registry, cr)

    # TOFIX
    @api.one
    def _set_tpl_sequence(self, generator_seq, item_tpl_seq):
        self._tpl_sequence = (
            int("{:0<4d}".format(generator_seq)) + item_tpl_seq)

    sequence = fields.Integer(
        string='Sequence', required=True, default=50,
        help="Gives the order in which the pricelist items will be checked"
             "by the ERP.\n"
             "The evaluation gives highest priority to lowest sequence and "
             "stops as soon as a matching price item is found.")
    base = fields.Selection(
        selection='_price_field_get', default=1,
        string='Based on', required=True, size=-1,
        help="Base price for computation.")
    price_surcharge = fields.Float(
        string='Price Surcharge',
        digits_compute=dp.get_precision('Product Price'),
        help='Specify the fixed amount to add or substract(if negative) to '
             'the amount calculated with the discount.')
    price_discount = fields.Float(
        string='Price Discount', digits=(16, 4), default=0)
    price_round = fields.Float(
        string='Price Rounding',
        digits_compute=dp.get_precision('Product Price'),
        help="Sets the price so that it is a multiple of this value.\n"
             "Rounding is applied after the discount and before the "
             "surcharge.\n To have prices that end in 9.99, "
             "set rounding 10, surcharge -0.01")
    price_min_margin = fields.Float(
        string='Min. Price Margin',
        digits_compute=dp.get_precision('Product Price'),
        help='Specify the minimum amount of margin over the base price.')
    price_max_margin = fields.Float(
        string='Max. Price Margin',
        digits_compute=dp.get_precision('Product Price'),
        help='Specify the maximum amount of margin over the base price.')

    @api.one
    @api.constrains('price_min_margin', 'price_max_margin')
    def _check_margin(self):
        if self.price_max_margin and self.price_min_margin and (
                self.price_min_margin > self.price_max_margin):
            raise UserError(_("Error! The minimum margin should be lower "
                              "than the maximum margin."))

    @api.model
    def _price_field_get(self):
        # TODO : allow other type of pricelist
        result = []
        result.append((1, _('Public Price')))
        return result


class PricelistItemTemplate(models.Model):
    """ This model is called by a second class
    """
    _inherit = ['abstract.pricelist.item.generator', 'pricelist.item.template']
    _name = 'pricelist.item.template'

    _order = 'sequence ASC, id ASC'

    price_generator_id = fields.Many2one(
        comodel_name='pricelist.item.generator', required=True)

    @api.multi
    def write(self, vals):
        self[0].price_generator_id.write({'to_update': True})
        return super(PricelistItemTemplate, self).write(vals)

    @api.multi
    def unlink(self):
        product_item_m = self.env['product.pricelist.item']
        product_item_m.search([('item_template_id', 'in', self.ids)]).unlink()
        return super(PricelistItemTemplate, self).unlink()


class ProductPricelistItem(models.Model):
    _inherit = ['abstract.pricelist.item.generator', 'product.pricelist.item']
    _name = 'product.pricelist.item'

    auto = fields.Boolean(
        string='Auto', default=False,
        help="If true, the item pricelist was built automatically "
             "with Pricelist")
    hashkey = fields.Char(
        string='Hashkey', readonly=True,
        help="Contains all price element values from Pricelist generator."
             "It allows to avoid to update price element when it's not "
             "necessary")
    item_template_id = fields.Many2one(
        comodel_name='pricelist.item.template',
        string='Item template', readonly=True)


class ProductPricelistVersion(models.Model):
    _inherit = 'product.pricelist.version'

    item_auto_ids = fields.One2many(
        comodel_name='product.pricelist.item',
        inverse_name='price_version_id',
        string='Pricelist items auto',
        domain=[('auto', '=', True)],
        help="Automatic built items")
    item_manual_ids = fields.One2many(
        comodel_name='product.pricelist.item',
        inverse_name='price_version_id',
        string='Pricelist items manual',
        domain=[('auto', '=', False)],
        help="Manually created items")
