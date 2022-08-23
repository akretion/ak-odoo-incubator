# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    invoice_link = fields.Char(compute="_compute_invoice_link", store=True)

    def _get_invoice_statement_pattern(self):
        """Inherit and complete this dict according to
        your companies invoice numbers.
        {company_id: [r"one_string_to_search", r"other_one"]}
        """
        return {1: [r"INV/\w+"]}

    @api.depends("payment_ref")
    def _compute_invoice_link(self):
        suffix = self._get_invoice_statement_pattern()
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            if rec.payment_ref and rec.company_id:
                suffixes = suffix.get(rec.company_id.id)
                inv_names = []
                inv_str = ""
                for suff in suffixes:
                    inv_str = re.findall(suff, rec.payment_ref)
                    inv_names.extend(inv_str)
                moves = []
                for name in inv_names:
                    move = self.env["account.move"].search([("name", "=", name)])
                    if move:
                        moves.append(move)
                if moves:
                    if len(moves) == 1:
                        inv_str = self._get_invoice_link(base_url, moves[0], rec)
                    else:
                        # Only descriptive string here
                        inv_str = "\n".join(
                            ["{} {}".format(x.date, x.name) for x in moves]
                        )
                else:
                    inv_str = ""
                rec.invoice_link = inv_str

    @staticmethod
    def _get_invoice_link(base_url, move, record):
        if base_url:
            return (
                '=HYPERLINK("%(url)s/web#id=%(id)s&model=account.move&'
                'view_type=form&cids=%(company_id)s"'
                % {"url": base_url, "id": move.id, "company_id": record.company_id.id}
                + ', "{} {}")'.format(move.date, move.name)
            )

        else:
            return move.name
