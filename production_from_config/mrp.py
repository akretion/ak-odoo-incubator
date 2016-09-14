# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien Beau <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _get_product_from_config(self, original_product_lines):
        self.ensure_one()
        return original_product_lines

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def _bom_explode(self, bom, product, factor, properties=None, level=0,
                     routing_id=False, previous_products=None,
                     master_bom=None):
        product_lines, workcenter_lines = super(
            MrpBom, self.with_context(subcall=True))._bom_explode(
                bom, product, factor,
                properties=properties, level=level,
                routing_id=routing_id, previous_products=previous_products,
                master_bom=master_bom)
        prod_obj = self.env['mrp.production']
        production_id = self.env.context.get('production_id')
        if production_id and not self.env.context.get('subcall', False):
            production = prod_obj.browse(production_id)
            new_product_lines = production._get_product_from_config(
                product_lines)
            del product_lines
            product_lines = new_product_lines
        return product_lines, workcenter_lines

