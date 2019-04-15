# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    support_uid = fields.Char()
    support_last_update_date = fields.Datetime()

    _sql_constraints = [
        (
            "support_uid_uniq",
            "unique (support_uid)",
            "Support UID already exist !",
        )
    ]
