# © 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class InvoiceWizard(models.TransientModel):
    _name = "wizard.holding.invoicing"

    date_invoice = fields.Date(
        "Invoice Date", required=True, default=fields.Datetime.now
    )
    team_id = fields.Many2one("crm.case.section", string="Sale Section", required=True)

    def _get_invoice_domain(self):
        self.ensure_one()
        return [
            ("team_id", "=", self.team_id.id),
            ("invoice_state", "=", "invoiceable"),
            ("holding_invoice_id", "=", False),
        ]

    def _return_open_action(self, invoices):
        action = self.env.ref("account.action_invoice_tree").read()[0]
        action.update(
            {
                "name": _("Invoice Generated"),
                "target": "current",
                "domain": [("id", "in", invoices.ids)],
            }
        )
        return action

    def create_invoice(self):
        self.ensure_one()
        domain = self._get_invoice_domain()
        invoices = self.env["holding.invoicing"]._generate_invoice(
            domain, date_invoice=self.date_invoice
        )
        if invoices:
            return self._return_open_action(invoices)
        else:
            raise UserError("There is not invoice to generate")
