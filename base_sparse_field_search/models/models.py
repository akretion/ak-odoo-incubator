# -*- coding: utf-8 -*-

from openerp import models, fields


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    sparse_search = fields.Boolean()
