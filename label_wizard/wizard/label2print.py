# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class LabelFromRecord(models.TransientModel):
    _name = 'label.from.record'

    @api.model
    def __get_label_content(self):
        return self._get_label_content()

    content = fields.Text(
        string=u"Label's content", default=__get_label_content)
    with_price = fields.Boolean(
        string=u"Print price",
        help=u"Print price on labels")

    @api.model
    def _get_label_content(self):
        product_infos = []
        model = self._context['active_model']
        if model == 'stock.picking':
            # PICKING
            if self._context.get('active_id'):
                moves = self.env['stock.move'].search([
                    ('picking_id', '=', self._context['active_id'])])
                product_infos = [
                    '%s ; %s ; %s' % (
                        x.product_id.default_code or '_',
                        int(x.product_uom_qty),
                        x.product_id.id)
                    for x in moves if x.product_id]
        else:
            # PRODUCT
            products = self.env[model].browse(self._context['active_ids'])
            product_infos = ['%s ; %s ; %s' % (
                             x.default_code or '_', 1, x.id)
                             for x in products]
        return '\n'.join(product_infos)

    @api.multi
    def generate_label(self):
        Product_m = self.env['product.product']
        for rec in self:
            if rec.content:
                products2print, data4print = [], []
                lines = rec.content.split('\n')
                for line in lines:
                    # on remplace le text par des entiers quand possible
                    # 0 est considéré comme False donc n'est pas
                    # transformé en entier
                    parts = [(x.strip().isdigit() and int(x.strip()) or
                              x.strip())
                             for x in line.split(';') if x.strip()]
                    rec._sanitize_and_check_parts(parts, line)
                    products2print.append(parts[:])
                for info in products2print:
                    product, quantity = rec._search_product(info)
                    if product:
                        data4print.append((product, quantity))
                if data4print:
                    return Product_m.get_labels_zebra(
                        data4print,
                        with_price=rec.with_price)
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def _search_product(self, info):
        """ info[0]: code, info[1]: quantity, info[2]: id
            return product, quantity
        """
        Product_m = self.env['product.product']
        if len(info) > 2:
            product = Product_m.search([('id', '=', info[2])])
            if product:
                return (Product_m.browse(info[2]), info[1])
        products = Product_m.search([('default_code', '=', info[0])])
        if products:
            return (product[0], info[1])
        return (False, False)

    @api.model
    def _sanitize_and_check_parts(self, parts, line):
        """ @return la 1ère règle non respecté
        """
        message = u"La ligne '%s' ne respecte pas le format."
        if not isinstance(parts, list):
            raise UserError(_(message % line))
        if len(parts) <= 2:
            raise UserError(_(message % line))
        if len(parts) >= 4:
            raise UserError(_(u"Plus de 3 segments. " + message % line))
        if not isinstance(parts[1], int):
            raise UserError(_(u"La quantité n'est pas un entier '%s'" % line))
        if parts[1] <= 0:
            raise UserError(_(u"La quantité ne peut être <= 0. '%s'" % line))
        if len(parts) > 2 and not isinstance(parts[2], int):
            raise UserError(_(u"L'id n'est pas un entier '%s'" % line))
        return True
