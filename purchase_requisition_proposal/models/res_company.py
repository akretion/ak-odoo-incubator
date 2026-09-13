# Copyright (C) 2023 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    requisition_intercompany_partner_ids = fields.Many2many(
        comodel_name="res.users",
        column1="company",
        column2="partners_to_send_mails",
        relation="company_rel_partners_to_send_mails",
        string="Requisition Intercompany Partners",
    )
