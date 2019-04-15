# -*- coding: utf-8 -*-
# Copyright 2012-2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields, models
from odoo.tools.translate import _


class AccountJournal(models.Model):
    _name = "account.journal"
    _inherit = ["account.journal"]

    import_type = fields.Selection(
        selection_add=[
            ("atos_csvparser", _("Parser for Atos/Sips (mercanet) xls file"))
        ]
    )
