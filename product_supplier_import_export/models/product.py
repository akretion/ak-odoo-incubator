# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp
from openerp.tools.config import config
from openerp.tools import ustr


class FloatNullEmpty(fields.Float):

    def convert_to_export(self, value, env):
        if value:
            return value if env.context.get('export_raw_data') else ustr(value)
        return ''


class ProductSupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.multi
    def _denormalized_update(self, vals):
        """ update the porudtc.supplierinof and the pricelist.partnerinfo
        if the data have change, if not change have been done skip the write"""
        self.ensure_one()
        pricelist_obj = self.env['pricelist.partnerinfo']
        sup_vals = {}
        for key in ['product_name', 'product_code', 'sequence']:
            if vals[key] != self[key]:
                sup_vals[key] = vals[key]
        if sup_vals:
            self.write(sup_vals)
        pricelists = pricelist_obj.browse(False)
        for idx in range(0, config.get('supplier_qty_export_nbr', 3)):
            qty = vals['qty_%s' % (idx + 1)]
            price = vals['price_%s' % (idx + 1)]
            pvals = {'min_quantity': qty, 'price': price}
            if len(self.pricelist_ids) > idx:
                p = self.pricelist_ids[idx]
                if not price and not qty:
                    continue
                elif p.price != price or p.min_quantity != qty:
                    p.write(pvals)
                pricelists |= p
            elif price and qty:
                pvals['suppinfo_id'] = self.id
                pricelists |= pricelist_obj.create(pvals)
        for p in self.pricelist_ids:
            if p not in pricelists:
                p.unlink()

    @api.model
    def _denormalized_create(self, vals):
        vals['pricelist_ids'] = []
        for idx in range(0, config.get('supplier_qty_export_nbr', 3)):
            qty = vals.pop('qty_%s' % (idx + 1))
            price = vals.pop('price_%s' % (idx + 1))
            if not qty and not price:
                # if empty skip it
                continue
            if idx == 0 and not qty:
                # If we only import price_1 we set by default the quantity
                # to 1 to allow simple import
                qty = 1
            vals['pricelist_ids'].append((0, 0, {
                'min_quantity': qty,
                'price': price,
                }))
        return self.create(vals)


class DenormalizedProductSupplier(models.AbstractModel):
    _name = "denormalized.product.supplier"

    @classmethod
    def _add_magic_fields(cls):
        sup_export_nbr = config.get('supplier_export_nbr', 3) + 1
        sup_qty_export_nbr = config.get('supplier_qty_export_nbr', 3) + 1
        for idx in range(1, sup_export_nbr):
            field_partner_id = fields.Many2one(
                'res.partner',
                compute='_compute_supplier',
                inverse='_set_supplier')
            field_code = fields.Char(
                compute='_compute_supplier',
                inverse='_set_supplier')
            field_name = fields.Char(
                compute='_compute_supplier',
                inverse='_set_supplier')
            cls._add_field('supplier_%s_product_code' % idx, field_code)
            cls._add_field('supplier_%s_product_name' % idx, field_name)
            cls._add_field('supplier_%s_name' % idx, field_partner_id)
            for qty_idx in range(1, sup_qty_export_nbr):
                field_price = FloatNullEmpty(
                    digits_compute=dp.get_precision('Product Price'),
                    compute='_compute_supplier',
                    inverse='_set_supplier')
                field_qty = FloatNullEmpty(
                    compute='_compute_supplier',
                    inverse='_set_supplier')
                cls._add_field(
                    'supplier_%s_qty_%s' % (idx, qty_idx), field_qty)
                cls._add_field(
                    'supplier_%s_price_%s' % (idx, qty_idx), field_price)
        return super(DenormalizedProductSupplier, cls)._add_magic_fields()

    @api.multi
    def _get_specific_supplier(self):
        self.ensure_one()
        return self.seller_ids

    def _compute_supplier(self):
        sup_export = config.get('supplier_export_nbr', 3)
        qty_export = config.get('supplier_qty_export_nbr', 3)
        for record in self:
            suppliers = record._get_specific_supplier()
            for idx, supplier in enumerate(suppliers):
                if idx >= sup_export:
                    break
                s_idx = idx + 1
                record['supplier_%s_name' % s_idx] = supplier.name
                record['supplier_%s_product_name' % s_idx] =\
                    supplier.product_name
                record['supplier_%s_product_code' % s_idx] =\
                    supplier.product_code
                for idx2, pricelist in enumerate(supplier.pricelist_ids):
                    if idx >= qty_export:
                        break
                    p_idx = idx2 + 1
                    record['supplier_%s_qty_%s' % (s_idx, p_idx)] =\
                        pricelist.min_quantity
                    record['supplier_%s_price_%s' % (s_idx, p_idx)] =\
                        pricelist.price

    @api.multi
    def _update_create_supplier(self, vals):
        self.ensure_one()
        supplier = self._get_supplier(vals['name'])
        if supplier:
            supplier._denormalized_update(vals)
        else:
            vals = self._prepare_supplier_vals(vals)
            supplier = self.env['product.supplierinfo'].\
                _denormalized_create(vals)
        return supplier

    @api.model
    def _prepare_supplier_vals(self, vals):
        vals['name'] = vals['name'].id
        return vals

    def _get_sequence(self, idx):
        return idx * 10

    @api.multi
    def _set_supplier(self):
        for record in self:
            suppliers = self.env['product.supplierinfo'].browse(False)
            for idx in range(1, config.get('supplier_export_nbr', 3) + 1):
                if not record['supplier_%s_name' % idx]:
                    continue
                suppliers |= record._update_create_supplier({
                    'sequence': self._get_sequence(idx),
                    'name': record['supplier_%s_name' % idx],
                    'product_name': record['supplier_%s_product_name' % idx],
                    'product_code': record['supplier_%s_product_code' % idx],
                    'qty_1': record['supplier_%s_qty_1' % idx],
                    'price_1': record['supplier_%s_price_1' % idx],
                    'qty_2': record['supplier_%s_qty_2' % idx],
                    'price_2': record['supplier_%s_price_2' % idx],
                    'qty_3': record['supplier_%s_qty_3' % idx],
                    'price_3': record['supplier_%s_price_3' % idx],
                    })
            for supplier in record._get_specific_supplier():
                if supplier not in suppliers:
                    supplier.unlink()


class ProductTemplate(models.Model):
    _inherit = ["product.template", "denormalized.product.supplier"]
    _name = 'product.template'

    @api.multi
    def _prepare_supplier_vals(self, vals):
        vals = super(ProductTemplate, self)._prepare_supplier_vals(vals)
        vals['product_tmpl_id'] = self.id
        return vals

    @api.multi
    def _get_specific_supplier(self):
        self.ensure_one()
        return [supplier for supplier in self.seller_ids
                if not supplier.product_id]

    @api.multi
    def _get_supplier(self, partner):
        self.ensure_one()
        for seller in self.seller_ids:
            if partner == seller.name and not seller.product_id:
                return seller
        return None

    def _get_sequence(self, idx):
        return 1000 + idx * 10


class ProductProduct(models.Model):
    _inherit = ["product.product", "denormalized.product.supplier"]
    _name = 'product.product'

    @api.multi
    def _prepare_supplier_vals(self, vals):
        vals = super(ProductProduct, self)._prepare_supplier_vals(vals)
        vals.update({
            'product_id': self.id,
            'product_tmpl_id': self.product_tmpl_id.id,
            })
        return vals

    @api.multi
    def _get_supplier(self, partner):
        self.ensure_one()
        for seller in self.seller_ids:
            if partner == seller.name and seller.product_id:
                return seller
        return None

    @api.multi
    def _get_specific_supplier(self):
        self.ensure_one()
        return [supplier for supplier in self.seller_ids
                if supplier.product_id]
