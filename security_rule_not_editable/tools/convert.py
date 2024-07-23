# Copyright 2021 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tools.convert import xml_import

ori_tag_record = xml_import._tag_record


def _tag_record(self, rec, extra_vals=None):
    noupdate = self._noupdate
    if rec.get("model") == "ir.rule":
        self._noupdate = [False]
    ori_tag_record(self, rec, extra_vals)
    if rec.get("model") == "ir.rule":
        self._noupdate = noupdate


xml_import._tag_record = _tag_record
