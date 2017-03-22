# -*- coding: utf-8 -*-

from openerp import models, fields, api

from openerp.addons.base.ir.ir_model import _get_fields_type


class TestSparse(models.TransientModel):
    _name = 'sparse_fields.test'

    data = fields.Serialized()
    boolean = fields.Boolean(sparse='data')
    integer = fields.Integer(sparse='data')
    float = fields.Float(sparse='data')
    char = fields.Char(sparse='data')
    selection = fields.Selection([('one', 'One'), ('two', 'Two')], sparse='data')
    partner = fields.Many2one('res.partner', sparse='data')
