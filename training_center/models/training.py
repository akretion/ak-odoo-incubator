# -*- coding: utf-8 -*-

from odoo import models, fields


class Training(models.Model):
    _name = 'training'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Training', required=True, track_visibility='onchange')
    quotation_id = fields.Many2one(
        comodel_name='sale.order', string='Quotation')
    content = fields.Text()
    trainer_id = fields.Many2one(
        comodel_name='res.partner', string='Trainer')
    state = fields.Selection(default='draft', selection=[
        ('draft', 'Draft'), ('approved', 'Approved'),
        ('done', 'Done'), ('cancelled', 'Cancelled')],
        track_visibility='onchange')
    auditor_ids = fields.Many2many(
        comodel_name='res.partner', string='Auditors')
    related_auditor_ids = fields.Many2many(
        related='auditor_ids', readonly=True)
    duration = fields.Integer('Duration')
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
