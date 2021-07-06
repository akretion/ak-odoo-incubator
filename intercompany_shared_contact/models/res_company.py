# Copyright 2021 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"

    _sql_constraints = [
        (
            "partner_uniq",
            "unique (partner_id)",
            "The company partner_id must be unique !",
        )
    ]
