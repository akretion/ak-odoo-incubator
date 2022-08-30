# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.misc import formatLang, format_date


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    origin_statement = fields.Char(compute="_compute_origin_statement")
    payment_origin = fields.Char(string="Payment", compute="_compute_payment_origin")

    def _compute_origin_statement(self):
        move_action = self.sudo().env.ref("account.action_move_journal_line")
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            debits, credits = [], []
            for line in rec.line_ids:
                deb_i = [
                    "Deb. %(date)s: %(amount)s, %(ref)s Pce %(pce)s id_%(id)s"
                    % {
                        "date": format_date(self.env, x.debit_move_id.date),
                        "amount": formatLang(
                            self.env,
                            x.amount,
                            currency_obj=x.company_id.currency_id,
                        ),
                        "ref": x.debit_move_id.ref or x.debit_move_id.name,
                        "pce": x.debit_move_id.move_id.ref,
                        "id": x.debit_move_id.move_id.id,
                    }
                    for x in line.matched_debit_ids
                ]
                if deb_i:
                    debits.extend(deb_i)
                cred_i = [
                    "Cred. %(date)s: %(amount)s, %(ref)s Pce %(pce)s Part %(part)s id_%(id)s"
                    % {
                        "date": format_date(self.env, x.credit_move_id.date),
                        "amount": formatLang(
                            self.env,
                            x.amount,
                            currency_obj=x.company_id.currency_id,
                        ),
                        "ref": x.credit_move_id.ref or x.credit_move_id.name,
                        "pce": x.credit_move_id.move_id.ref,
                        "part": x.credit_move_id.move_id.partner_id
                        and x.credit_move_id.move_id.partner_id.name,
                        "id": x.credit_move_id.move_id.id,
                    }
                    for x in line.matched_credit_ids
                ]
                if cred_i:
                    credits.extend(cred_i)
            debits.extend(credits)
            if len(debits) == 1:
                rec.origin_statement = self._get_spreadsheet_link(
                    base_url, move_action, debits[0]
                )
            else:
                rec.origin_statement = ";\n".join(debits)

    @api.model
    def _get_spreadsheet_link(self, base_url, action, string):
        if base_url:
            model = action.res_model
            if not isinstance(string, str):
                id_ = string
                string = "paiem"
            else:
                id_ = string[string.index("id_") + 3 :]
                id_ = self.sudo().env[model].browse(int(id_))
            if hasattr(id_, "id"):
                return (
                    '=HYPERLINK("%(url)s/web#id=%(id)s&action=%(action)s&'
                    'model=%(model)s&view_type=form&cids=1"'
                    # 'model=%(model)s&view_type=form&cids=%(company_id)s"'
                    % {
                        "url": base_url,
                        "id": id_.id,
                        "model": model,
                        "action": action and action.id,
                        # "company_id": id_.company_id.id,
                    }
                    + ', "%(name)s")'
                    % {
                        "name": "🔗 " + string,
                    }
                )
        return string

    def _compute_payment_origin(self):
        action = self.sudo().env.ref("account.action_account_payments_payable")
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
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
            docs = {line: pay[re] for line, re in line_rec.items() if re in pay}
            if docs:
                for __, payment in docs.items():
                    rec.payment_origin = self._get_spreadsheet_link(
                        base_url,
                        action,
                        payment
                    )
                    break
            else:
                rec.payment_origin = ""
