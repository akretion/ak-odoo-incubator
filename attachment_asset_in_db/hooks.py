# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    cr.execute("""
        SELECT id
        FROM ir_attachment
        WHERE db_datas IS NULL
        AND (name='web_icon_data' OR name ilike '/web/content/%')""")
    ids = [x[0] for x in cr.fetchall()]
    env = api.Environment(cr, SUPERUSER_ID, {})
    for attachment in env["ir.attachment"].browse(ids):
        attachment.write({"datas": attachment.datas})
