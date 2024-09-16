# Copyright 2023 Akretion (https://www.akretion.com).
# @author Chafique Delli <chafique.delli@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def cancel(self):
        for record in self:
            if record.state == "opening_control":
                record.check_access_rights("write")
                record.check_access_rule("write")
                for statement in record.statement_ids:
                    statement.pos_session_id = None
                    statement.unlink()
                record.sudo().unlink()
        return {
            "type": "ir.actions.client",
            "name": "Point of Sale",
            "tag": "reload",
            "params": {
                "menu_id": self.env.ref("pos_sale_order.menu_pos_sale_order_root").id
            },
        }
