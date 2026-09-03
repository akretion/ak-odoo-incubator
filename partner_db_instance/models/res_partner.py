# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    instance_ids = fields.One2many(
        "res.partner.instance",
        "partner_id",
        string="Instances",
    )
    instance_id = fields.Many2one(
        "res.partner.instance",
        compute="_compute_instance_id",
        store=True,
    )

    @api.constrains("instance_ids")
    def _check_instance_ids(self):
        for partner in self:
            if len(partner.instance_ids) > 1:
                raise ValidationError(
                    self.env._("A partner can only have one active instance.")
                )

    @api.depends("instance_ids")
    def _compute_instance_id(self):
        for partner in self:
            partner.instance_id = partner.instance_ids[:1]

    def action_create_partner_db_instance(self):
        self.ensure_one()
        new_instance = self.env["res.partner.instance"].create(
            {
                "partner_id": self.id,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner.instance",
            "view_mode": "form",
            "res_id": new_instance.id,
        }

    def action_view_instance(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner.instance",
            "view_mode": "form",
            "res_id": self.instance_id.id,
        }
