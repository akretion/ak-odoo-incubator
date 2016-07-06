# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    weight_ratio = fields.Float(
        string='Weight Ratio',
        help="Coefficient between weight net and weight gross.\n"
             "i.e. if I set 1.05, default weight gross is 5 % upper "
             "than weight net")
