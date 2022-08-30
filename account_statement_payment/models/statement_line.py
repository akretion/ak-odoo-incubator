# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.misc import formatLang, format_date


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    reconciled_info = fields.Char(compute="_compute_reconciled_info")

    def _get_spreadsheet_link(self, base_url, action, rec, string):
        model = action.res_model
        return (
            '=HYPERLINK("%(url)s/web#id=%(id)s&action=%(action)s&'
            'model=%(model)s&view_type=form&cids=1"'
            # 'model=%(model)s&view_type=form&cids=%(company_id)s"'
            % {
                "url": base_url,
                "id": rec.id,
                "model": model,
                "action": action and action.id,
                # "company_id": id_.company_id.id,
            }
            + ', "%(text)s")'
            % {
                "text": "🔗 " + string,
            }
        )

    def _get_reconciled_info(self, base_url, action, reconciled):
        msg = []
        reconciled_info = ""
        for amount, line_id in reconciled:
            move = line_id.move_id
            curr_id = line_id.company_id.currency_id
            name = move.name + " (" + move.ref + ")" if move.ref else move.name
            msg.append(
                "%(amount)s: %(name)s %(date)s id_%(id)s"
                % {
                    "amount": formatLang(self.env, amount, currency_obj=curr_id),
                    "name": name,
                    "date": format_date(self.env, line_id.date),
                    "id": move.id,
                }
            )

        if len(msg) == 1:
            rec = reconciled[0][1].move_id
            # hyperlink to account.payment if move is a payment
            if rec.payment_id:
                rec = rec.payment_id
                action = self.sudo().env.ref("account.action_account_payments_payable")
            reconciled_info = self._get_spreadsheet_link(base_url, action, rec, msg[0])
        else:
            reconciled_info = ";\n".join(msg)
        return reconciled_info

    def _compute_reconciled_info(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        action = self.sudo().env.ref("account.action_move_journal_line")
        for rec in self:
            reconciled = []
            for line in rec.line_ids:
                for matched_debit_id in line.matched_debit_ids:
                    reconciled.append(
                        (matched_debit_id.amount, matched_debit_id.debit_move_id)
                    )
                for matched_credit_id in line.matched_credit_ids:
                    reconciled.append(
                        (matched_credit_id.amount, matched_credit_id.credit_move_id)
                    )

            rec.reconciled_info = self._get_reconciled_info(
                base_url, action, reconciled
            )