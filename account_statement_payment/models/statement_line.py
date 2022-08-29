# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

ACTION = False
SALE = False
PURCHASE = False


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    origin_statement = fields.Char(compute="_compute_origin_statement")

    def _compute_origin_statement(self):
        global ACTION, SALE, PURCHASE
        if not ACTION:
            ACTION = self.sudo().env.ref(
                "account.action_account_payments_payable", raise_if_not_found=False
            )
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        # Sale or purchase modules may be not both installed,
        # we have to check outside of the loop and defined in a global scope
        if "sale.order" in self.env.registry.models.keys():
            SALE = "sale"
        if "purchase.order" in self.env.registry.models.keys():
            PURCHASE = "purchase"
        for rec in self:
            rec_lines = rec.move_id.line_ids.filtered(lambda s: s.full_reconcile_id)
            line_rec = {
                x: x.full_reconcile_id
                for x in rec.move_id.line_ids.filtered(lambda s: s.full_reconcile_id)
            }
            reconc = self.env["account.move.line"].search(
                [
                    (
                        "full_reconcile_id",
                        "in",
                        rec_lines.mapped("full_reconcile_id").ids,
                    ),
                ]
            )
            pay = {
                x.full_reconcile_id: x.mapped("payment_id")
                for x in reconc.filtered(lambda s: s.payment_id)
            }
            line_docs = {
                line: "%s, %s %s %s %s"
                % (
                    pay[re].amount,
                    pay[re].ref or pay[re].name,
                    pay[re].partner_id and pay[re].partner_id.name,
                    self._get_commercial_record_name(pay[re], "sale")
                    or self._get_commercial_record_name(pay[re], "purchase"),
                    "pay_id%s" % pay[re].id,
                )
                for line, re in line_rec.items()
                if re in pay
            }
            if line_docs:
                strings = []
                for line, val in line_docs.items():
                    strings.append(val)
                if len(strings) == 1:
                    rec.origin_statement = self._get_payment_link(
                        base_url,
                        ACTION,
                        val,
                    )
                else:
                    rec.origin_statement = "\n".join(strings)
            else:
                rec.origin_statement = ""

    @api.model
    def _get_commercial_record_name(self, payment, record_type):
        """Redirect towards the right fields according to installed modules: sale or purchase"""
        if record_type == SALE:
            return payment.sale_id and payment.sale_id.name or ""
        if record_type == PURCHASE:
            return payment.purchase_id and payment.purchase_id.name or ""
        return ""

    @api.model
    def _get_payment_link(self, base_url, action, string):
        if base_url:
            payment = string[string.index("pay_id") + 6 :]
            payment = self.sudo().env["account.payment"].browse(int(payment))
            if hasattr(payment, "id"):
                return (
                    '=HYPERLINK("%(url)s/web#id=%(id)s&action=%(action)s&'
                    'model=account.payment&view_type=form&cids=%(company_id)s"'
                    % {
                        "url": base_url,
                        "id": payment.id,
                        "action": action and action.id,
                        "company_id": payment.company_id.id,
                    }
                    + ', "%(name)s")'
                    % {
                        "name": "🔗 " + string,
                    }
                )
        return string
