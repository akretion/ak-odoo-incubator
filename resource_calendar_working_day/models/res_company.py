# coding: utf-8
# Copyright (C) 2018 AKRETION (<http://www.akretion.com>).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    calendar_id = fields.Many2one(
        "resource.calendar", string="Company Working time"
    )
