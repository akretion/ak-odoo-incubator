# coding: utf-8
# © 2018 Raphaël REVERDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    description_website = fields.Text(
        string='E-commerce description',
        translate=True,
        help="This description will be displayed on the e-commerce website.")
    description_short = fields.Char(
        string=u"Short description", translate=True,
        help=u"This description will be displayed on the e-commerce website.",
        oldname="short_description")
