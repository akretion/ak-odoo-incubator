# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from openerp.tools import ustr
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
try:
    from unidecode import unidecode  # Debian package python-unidecode
except (ImportError, IOError) as err:
        _logger.debug(err)


def safe_column_name(string):
    """This function prevent portability problem in database column name
    with other DBMS system
    Use case : if you synchronise attributes with other applications """
    string = unidecode(string.replace(' ', '_').lower())
    return re.sub(r'[^0-9a-z_]', '', string)


class FloatDynamicPrice(fields.Float):
    _dynamic_price = True

    def convert_to_export(self, value, env):
        if value:
            return value if env.context.get('export_raw_data') else ustr(value)
        return ''


class IrFieldsConverter(models.Model):
    _inherit = 'ir.fields.converter'

    @api.model
    def _str_to_float(self, model, field, value):
        # Add comma support for float
        value = value.replace(',', '.')
        return super(IrFieldsConverter, self)._str_to_float(
            model, field, value)


class DenormalizedProductPricelist(models.AbstractModel):
    _name = "denormalized.product.pricelist"

    @classmethod
    def _init_manual_fields(cls, cr, partial):
        cr.execute("""SELECT
            CONCAT(c.name, ' : ', pv.name),
            pv.name,
            pv.id
            FROM product_pricelist_version AS pv
            JOIN res_company AS c
                ON c.id=pv.company_id
            JOIN product_pricelist AS p
                ON p.id = pv.pricelist_id
            WHERE p.type = 'sale' and p.price_grid = True""")
        for fullname, name, id in cr.fetchall():
            field_name = safe_column_name('price_%s_%s' % (id, name))
            field_price = FloatDynamicPrice(
                name="%s %s" % (_("Price"), fullname),
                digits_compute=dp.get_precision('Product Price'),
                compute='_compute_price',
                inverse='_set_price')
            cls._add_field(field_name, field_price)
        return super(DenormalizedProductPricelist, cls).\
            _init_manual_fields(cr, partial)

    @api.multi
    def _get_pricelist_grid_item_domain(self, pricelist_version_id):
        return [
            ('price_version_id', '=', pricelist_version_id),
            ]

    @api.multi
    def _get_pricelist_version(self, field_name):
        return int(field_name.split('_')[1])

    @api.multi
    def _get_pricelist_grid_item(self, field_name):
        pv_id = self._get_pricelist_version(field_name)
        domain = self._get_pricelist_grid_item_domain(pv_id)
        price_item = self.env['product.pricelist.item'].search(domain)
        if price_item:
            return price_item[0]
        else:
            return None

    @api.multi
    def _compute_price(self):
        field_names = [
            field_name for field_name in self._fields
            if (hasattr(self._fields[field_name], '_dynamic_price') and
                self._fields[field_name]._dynamic_price)]
        for record in self:
            for field_name in field_names:
                item = record._get_pricelist_grid_item(field_name)
                if item:
                    record[field_name] = item.price_surcharge
                else:
                    record[field_name] = None

    @api.model
    def create(self, vals):
        return super(DenormalizedProductPricelist,
                     self.with_context(write_keys=vals.keys())).create(vals)

    @api.multi
    def write(self, vals):
        return super(DenormalizedProductPricelist,
                     self.with_context(write_keys=vals.keys())).write(vals)

    @api.multi
    def _prepare_pricelist_item(self, field_name, value):
        # TODO use default value from pricelist_per_product after refactor
        pv_id = self._get_pricelist_version(field_name)
        return {
            'price_version_id': pv_id,
            'price_discount': -1,
            'price_surcharge': value,
            'sequence': 1,
            'base': 1,
            }

    @api.multi
    def _update_pricelist_item(self, field_name):
        item = self._get_pricelist_grid_item(field_name)
        value = self[field_name]
        if value:
            if item:
                item.write({'price_surcharge': self[field_name]})
            else:
                vals = self._prepare_pricelist_item(field_name, value)
                self.env['product.pricelist.item'].create(vals)
        elif item:
            item.unlink()

    @api.multi
    def _set_price(self):
        self.ensure_one()
        # FIXME Refactor with line 90
        field_names = [
            field_name for field_name in self._fields
            if (hasattr(self._fields[field_name], '_dynamic_price') and
                self._fields[field_name]._dynamic_price and
                field_name in self._context['write_keys'])]
        for field_name in field_names:
            self._update_pricelist_item(field_name)


class ProductTemplate(models.Model):
    _inherit = ["product.template", "denormalized.product.pricelist"]
    _name = 'product.template'

    @api.multi
    def _get_pricelist_grid_item_domain(self, pricelist_version_id):
        res = super(ProductTemplate, self).\
            _get_pricelist_grid_item_domain(pricelist_version_id)
        res += [
            ('product_tmpl_id', '=', self.id),
            ('product_id', '=', False),
            ]
        return res

    @api.multi
    def _prepare_pricelist_item(self, field_name, value):
        res = super(ProductTemplate, self).\
            _prepare_pricelist_item(field_name, value)
        res['product_tmpl_id'] = self.id
        return res


class ProductProduct(models.Model):
    _inherit = ["product.product", "denormalized.product.pricelist"]
    _name = 'product.product'

    @api.multi
    def _get_pricelist_grid_item_domain(self, pricelist_version_id):
        res = super(ProductProduct, self).\
            _get_pricelist_grid_item_domain(pricelist_version_id)
        res.append(('product_id', '=', self.id))
        return res

    @api.multi
    def _prepare_pricelist_item(self, field_name, value):
        res = super(ProductProduct, self).\
            _prepare_pricelist_item(field_name, value)
        res.update({
            'product_tmpl_id': self.product_tmpl_id.id,
            'product_id': self.id,
            })
        return res
