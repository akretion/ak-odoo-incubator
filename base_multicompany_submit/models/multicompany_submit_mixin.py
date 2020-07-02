#  Copyright (c) Akretion 2020
#  License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html)

from odoo import api, fields, models


class BaseMulticompanyMixin(models.AbstractModel):
    _name = "base.multicompany.mixin"
    _description = "Base mixin for multicompany submittal"

    state_multicompany_submit = fields.Selection(
        [
            ("not_submitted", "Not submitted"),
            ("pending_approval", "Pending approval"),
            ("approved", "Approved"),
            ("refused", "Refused"),
        ],
        default="not_submitted",
        string="Multicompany submittal state",
        track_visibility="onchange",
    )

    multicompany_origin_company_id = fields.Many2one(
        "res.company", string="Origin company", ondelete="set null"
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.multicompany_origin_company_id = res.company_id
        return res

    def action_make_multicompany(self):
        raise NotImplementedError

    def button_multicompany_submit(self):
        self.ensure_one()
        self.state_multicompany_submit = "pending_approval"

    def button_multicompany_approve(self):
        self.ensure_one()
        self.action_make_multicompany()
        self.state_multicompany_submit = "approved"

    def button_multicompany_refuse(self):
        self.ensure_one()
        self.state_multicompany_submit = "refused"

    def button_multicompany_cancel(self):
        self.ensure_one()
        self.state_multicompany_submit = "not_submitted"
