# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CertificatTypology(models.Model):
    _name = "certificat.typology"
    _description = "Certificat Typology"

    name = fields.Char(string="Name", required=True, translate=True)
    description = fields.Char(string="Description", translate=True)
    storage_duration = fields.Integer(
        string="Storage duration", help="Enter the number of days to keep the document."
    )
    automatic_deletion = fields.Selection(
        [
            ("none", "None"),
            ("x_day_after_so_confirm", "after SO confirmation"),
        ],
        string="Automatic deletion",
        default="none",
    )
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
