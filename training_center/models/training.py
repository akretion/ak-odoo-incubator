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
    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Customer',
        related='quotation_id.partner_id')
    trainer_id = fields.Many2one(
        comodel_name='res.partner', string='Trainer')
    training_place_id = fields.Many2one(
        comodel_name='res.partner', string='Place',
        help="If not specified, company address is used in the report)")
    training_place_cpt_id = fields.Many2one(
        comodel_name='res.partner', compute='_compute_place')
    state = fields.Selection(default='draft', selection=[
        ('draft', 'Draft'), ('approved', 'Approved'),
        ('done', 'Done'), ('cancelled', 'Cancelled')],
        track_visibility='onchange')
    auditor_ids = fields.Many2many(
        comodel_name='res.partner', string='Auditors')
    auditor_number = fields.Integer(compute='_compute_auditors')
    related_auditor_ids = fields.Many2many(
        related='auditor_ids', readonly=True)
    duration = fields.Integer(string='Duration')
    hour_number = fields.Integer(compute='_compute_hours')
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    company_id = fields.Many2one(
        comodel_name='res.company', string='Company')

    def _compute_place(self):
        for rec in self:
            if rec.training_place_id:
                rec.training_place_cpt_id = rec.training_place_id
            else:
                rec.training_place_cpt_id = rec.company_id.partner_id

    def _compute_hours(self):
        for rec in self:
            rec.hour_number = rec.duration * 7

    def _compute_auditors(self):
        for rec in self:
            rec.auditor_number = len(rec.auditor_ids)
