# -*- coding: utf-8 -*-
# © <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = ["product.product"]

    variant_configuration = fields.Char(
        compute='_compute_variant_configuration',
        inverse='_set_variant_configuration')

    @api.multi
    def _compute_variant_configuration(self):
        for record in self:
            record.variant_configuration = "\n".join([
                ":".join([value.attribute_id.name, value.name])
                for value in record.attribute_value_ids])

    @api.multi
    def _set_variant_configuration(self):
        # TODO add inverse fonction
        pass

    @api.multi
    def _get_default_fields(self, fields):
        template_fields = self.env['product.template']._fields
        default_fields = []
        for field in fields:
            if (len(field) == 1
                    and field[0] in template_fields
                    and field[0] != 'id'):
                default_fields.append(field)
        return default_fields

    @api.multi
    def _get_default_row(self, fields, default_fields):
        row = self[0].product_tmpl_id._export_rows(default_fields)[0]
        for idx, field in enumerate(fields):
            if not field in default_fields:
                if field and field[0] == 'variant_configuration':
                    row.insert(idx, 'default')
                else:
                    row.insert(idx, '')
        return row

    @api.multi
    def _export_rows(self, fields):
        data = super(ProductProduct, self)._export_rows(fields)
        if (['variant_configuration'] in fields
                and self._context.get('from_template_id')
                and len(self) > 1):
            default_fields = self._get_default_fields(fields)
            if default_fields:
                default = self._get_default_row(fields, default_fields)
                data.insert(0, default)
        return data


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _export_rows(self, fields):
        data = []
        for record in self:
            data += super(
                ProductTemplate,
                record.with_context(from_template_id=record.id)
                )._export_rows(fields)
        return data

    @api.model
    def _get_variant_id_from_configuration(
            self, tmpl_id, variant_configuration):
        product_obj = self.env['product.product']
        domain = [('product_tmpl_id', '=', tmpl_id)]
        value_obj = self.env['product.attribute.value']
        for option in variant_configuration.split('\n'):
            attribute_name, value_name = option.split(':')
            value = value_obj.search([
                ('attribute_id', '=', attribute_name),
                ('name', '=', value_name),
                ])
            domain.append(('attribute_value_ids', '=', value.id))
        product = product_obj.search(domain)
        return product.id

    @api.model
    def _update_product_ids_from_configuration(self, record):
        if record.get('.id'):
            tmpl_id = record['.id']
        elif record.get('id'):
            xml_id = record['id']
            if not '.' in xml_id:
                xml_id = u'.' + xml_id
            __, __, tmpl_id = self.env['ir.model.data'].xmlid_lookup(xml_id)
        else:
            # If there is not template id then we can not look at the variant
            return
        for variant in record['product_variant_ids']:
            variant_id = self._get_variant_id_from_configuration(
                tmpl_id, variant['variant_configuration'])
            if variant_id:
                variant.pop('variant_configuration')
                variant['.id'] = variant_id

    @api.model
    def _process_default_template_value(self, record):
        for variant in list(record['product_variant_ids']):
            if variant['variant_configuration'] == 'default':
                variant.pop('variant_configuration')
                record.update(variant)
                record['product_variant_ids'].remove(variant)
                break

    @api.model
    def _extract_records(self, fields_, data,
                         context=None, log=lambda a: None):
        for record, rows in super(ProductTemplate, self)._extract_records(
                fields_, data, context=context, log=log):
            if (['product_variant_ids', 'variant_configuration'] in fields_
                    and (['id'] in fields_ or ['.id'] in fields_)
                    and not ['product_variant_ids', 'id'] in fields_
                    and not ['product_variant_ids', 'id'] in fields_):
                self._process_default_template_value(record)
                self._update_product_ids_from_configuration(record)
            yield record, rows
