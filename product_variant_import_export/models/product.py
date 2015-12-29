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
