# © 2015 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Chafique Delli <chafique.delli@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    holding_company_id = fields.Many2one(
        "res.company",
        related="team_id.holding_company_id",
        string="Holding Company for Invoicing",
    )
    holding_invoice_id = fields.Many2one(
        "account.invoice",
        string="Holding Invoice",
        copy=False,
        readonly=True,
    )
    holding_invoice_state = fields.Selection(
        [
            ("none", "Not Applicable"),
            ("not_ready", "Not Ready"),
            ("invoiceable", "Invoiceable"),
            ("pending", "Pending"),
            ("invoiced", "Invoiced"),
        ],
        string="Holding Invoice State",
        compute="_compute_invoice_state",
        store=True,
    )

    # TODO
    # @api.depends("shipped", "team_id.holding_company_id")
    def _compute_invoice_state(self):
        # TODO
        return
        # Note for perf issue the 'holding_invoice_id.state' is not set here
        # as a dependency. Indeed the dependency is manually triggered when
        # the holding_invoice is generated or the state is changed
        for sale in self:
            if not sale.team_id.holding_company_id:
                sale.invoice_state = "none"
            elif sale.holding_invoice_id:
                if sale.holding_invoice_id.state in ("open", "paid"):
                    sale.invoice_state = "invoiced"
                else:
                    sale.invoice_state = "pending"
            elif sale.shipped:
                sale.invoice_state = "invoiceable"
            else:
                sale.invoice_state = "not_ready"

    def _set_invoice_state(self, state):
        if self:
            self._cr.execute(
                """UPDATE sale_order
                SET invoice_state=%s
                WHERE id in %s""",
                (state, tuple(self.ids)),
            )
            self.invalidate_cache()

    @api.onchange("team_id")
    def onchange_team_id(self):
        if self.team_id and self.team_id.holding_company_id:
            self.order_policy = "manual"
