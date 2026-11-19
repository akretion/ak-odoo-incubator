# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    def _lookup_xmlids(self, xml_ids, model):
        res = super()._lookup_xmlids(xml_ids, model)
        if model._name == "ir.rule":
            # Make xml updatable
            return [item[0:5] + (False,) + item[6:] for item in res]
        else:
            return res
