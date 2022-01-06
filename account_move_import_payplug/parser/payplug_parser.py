###############################################################################
#   account_statement_be2bill for OpenERP
#   Copyright (C) 2014-TODAY Akretion <http://www.akretion.com>.
#   @author Arthur Vuillard <arthur.vuillard@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from csv import Dialect

from _csv import QUOTE_MINIMAL, register_dialect

from odoo.addons.account_move_base_import.parser.file_parser import (
    FileParser,
    float_or_zero,
)


class payplug_dialect(Dialect):
    delimiter = ","
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = "\n"
    quoting = QUOTE_MINIMAL


register_dialect("payplug_dialect", payplug_dialect)


class PayplugFileParser(FileParser):
    def __init__(self, journal, ftype="csv", **kwargs):
        conversion_dict = {
            "Montant": float_or_zero,
            "Date": str,
            "ID API": str,
            "Description": str,
            "E-mail": str,
            "Type": str,
        }
        super().__init__(
            journal,
            ftype=ftype,
            extra_fields=conversion_dict,
            dialect=payplug_dialect,
            **kwargs
        )

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is be2bill_csvparser
        """
        return parser_name == "payplug_csvparser"

    def _pre(self, *args, **kwargs):
        super(PayplugFileParser, self)._pre(*args, **kwargs)
        split_file = self.filebuffer.decode().split("\n")
        selected_lines = []
        for line in split_file:
            if line.startswith("sep"):
                continue
            selected_lines.append(line.strip())
        self.filebuffer = "\n".join(selected_lines).encode()

    def get_move_line_vals(self, line, *args, **kwargs):
        if line["ID API"].startswith("re"):
            transaction_ref = ""
            ref = line["ID API"] + " %s" % line.get("E-mail")
        else:
            ref = line["ID API"] or line["Description"]
            transaction_ref = line["ID API"]
        res = {
            "ref": transaction_ref,
            "name": ref,
            "date_maturity": line["Date"],
            "credit": line["Montant"] > 0.0 and line["Montant"] or 0.0,
            "debit": line["Montant"] < 0.0 and abs(line["Montant"]) or 0.0,
        }
        # Put transfer in the waiting account to be reconciled with bank
        # statement. This way it is not mixed with counterparts
        if line.get("Type", "") == "Virement":
            res['account_id'] = self.journal.suspense_account_id.id
            res['partner_id'] = self.journal.partner_id.id or False
            res['already_completed'] = True
        if line.get("Type", "") == "Facture":
            partner = self.journal.partner_id
            res['account_id'] = partner.property_account_payable_id.id
            res['partner_id'] = partner.id
            if partner:
                res['already_completed'] = True
        return res

    def _post(self, *args, **kwargs):
        super(PayplugFileParser, self)._post(*args, **kwargs)
        for row in self.result_row_list:
            if not self.move_date or row["Date"] > self.move_date:
                self.move_date = row["Date"]
