# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    discount = fields.Selection([
        ('5', '5'),
        ('10', '10'),
        ('15', '15'),
        ('25', '25'),
        ('35', '35'),
        ('40', '40'),
        ('45', '45'),
        ('50', '50'),
        ])
