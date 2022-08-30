# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.misc import formatLang, format_date

SALE = False
PURCHASE = False


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    origin_statement = fields.Char(compute="_compute_origin_statement")
    origin_old = fields.Char(compute="_compute_origin_old")

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

    @api.model
    def _get_commercial_record_name(self, payment, record_type):
        """Redirect towards the right fields according to
        installed modules: sale or purchase"""
        if record_type == SALE:
            return payment.sale_id and payment.sale_id.name or ""
        if record_type == PURCHASE:
            return payment.purchase_id and payment.purchase_id.name or ""
        return ""

    def _compute_origin_old(self):
        global SALE, PURCHASE
        # Sale or purchase modules may be not both installed,
        # we have to check outside of the loop and defined in a global scope
        if "sale.order" in self.env.registry.models.keys():
            SALE = "sale"
        if "purchase.order" in self.env.registry.models.keys():
            PURCHASE = "purchase"
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
            docs = {
                line: "%s, %s %s %s %s"
                % (
                    pay[re].amount,
                    pay[re].ref or pay[re].name,
                    pay[re].partner_id and pay[re].partner_id.name,
                    self._get_commercial_record_name(pay[re], "sale")
                    or self._get_commercial_record_name(pay[re], "purchase"),
                    "id_%s" % pay[re].id,
                )
                for line, re in line_rec.items()
                if re in pay
            }
            if docs:
                strings = []
                for __, val in docs.items():
                    strings.append(val)
                if len(strings) == 1:
                    rec.origin_old = self._get_spreadsheet_link(
                        base_url,
                        action,
                        val,
                    )
                else:
                    rec.origin_old = "\n".join(strings)
            else:
                rec.origin_old = ""
