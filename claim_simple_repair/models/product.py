# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.osv import fields, orm


class ProductTemplate(orm.Model):
    _inherit = 'product.template'

    _columns = {
        'rma': fields.boolean(string='RMA'),
        'rma_in_description' : fields.text(
            string='RMA in description',
            translate=True),
        'rma_out_description' : fields.text(
            string='RMA out description',
            translate=True),
    }
