# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AbstractPartnerInfo(models.AbstractModel):
    _name = 'abstract.partner.comment'

    partner_comment = fields.Text(
        compute='_compute_partner_comment',
        help="Display comment from partner or partner parent "
             "in sale and picking")

    @api.multi
    def _compute_partner_comment(self):
        for rec in self:
            info = (rec.partner_id and rec.partner_id.parent_id and
                    rec.partner_id.parent_id.comment or
                    rec.partner_id.comment)
            if info:
                rec.partner_comment = info


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'abstract.partner.comment']
    _name = 'sale.order'


class StockPicking(models.Model):
    _inherit = ['stock.picking', 'abstract.partner.comment']
    _name = 'stock.picking'
