# Copyright (C) 2023 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class InterCompanyRulesConfig(models.TransientModel):
    _inherit = "res.config.settings"

    requisition_intercompany_partner_ids = fields.Many2many(
        comodel_name="res.users",
        string="Requisition Intercompany Partners",
        related="company_id.requisition_intercompany_partner_ids",
        readonly=False,
    )
