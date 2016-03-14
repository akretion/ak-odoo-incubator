# -*- coding: utf-8 -*-
# © 2016 Chafique DELLI @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class CrmCaseSection(models.Model):
    _inherit = 'crm.case.section'

    company_ids = fields.Many2many(
        'res.company',
        string='Companies',
        help="Add the companies concerned by this market.")
