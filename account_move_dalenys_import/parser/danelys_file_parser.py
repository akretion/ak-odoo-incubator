# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import codecs
from csv import Dialect

from _csv import QUOTE_MINIMAL, register_dialect

from odoo.addons.account_move_base_import.parser.file_parser import (
    FileParser,
    float_or_zero,
)


class DanelysDialect(Dialect):
    delimiter = ";"
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = "\n"
    quoting = QUOTE_MINIMAL


register_dialect("danelys_dialect", DanelysDialect)


class DanelysFileParser(FileParser):
    def __init__(self, journal, ftype="csv", **kwargs):
        conversion_dict = {
            "ORDERID": str,
            "AMOUNT": float_or_zero,
            "BILLINGFEES INCL. VAT": float_or_zero,
            "TRANSACTIONID": str,
            "EXECCODE": str,
        }
        super().__init__(
            journal,
            ftype=ftype,
            extra_fields=conversion_dict,
            dialect=DanelysDialect,
            **kwargs
        )

    def _pre(self, *args, **kwargs):
        super()._pre(*args, **kwargs)
        split_file = self.filebuffer.split(b"\n")
        selected_lines = []
        for line in split_file:
            if line.startswith(codecs.BOM_UTF8):
                line = line[3:]
            selected_lines.append(line.strip())
        self.filebuffer = b"\n".join(selected_lines)

    def get_move_line_vals(self, line, *args, **kwargs):
        amount = line["AMOUNT"]
        if line["OPERATIONTYPE"] == "refund":
            amount *= -1
        res = {
            "name": line.get("ORDERID", ""),
            "date_maturity": line.get("DATE"),
            "credit": amount > 0.0 and amount or 0.0,
            "debit": amount < 0.0 and -amount or 0.0,
        }
        return res


class DanelysPaypalAmexeParser(DanelysFileParser):
    def __init__(self, journal, ftype="csv", **kwargs):
        super().__init__(journal, ftype=ftype, **kwargs)
        self.support_multi_moves = True
        self._moves = None

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == "danelys_amex_paypal_csvparser"

    def _pre(self, *args, **kwargs):
        super()._pre(*args, **kwargs)
        res = self._parse_csv()
        self._moves = []
        for row in res:
            if row["EXECCODE"] in ("0", "0000"):
                self._moves.append(row)
        if self._moves:
            self.move_date = self._moves[0]["DATE"]

    def _parse(self, *args, **kwargs):
        """
        Implement a method in your parser to save the result of parsing
        self.filebuffer in self.result_row_list instance property.
        """
        if self._moves:
            move = self._moves.pop(0)
            self.result_row_list = [move]
            return True
        else:
            return False


class DanelysCBFileParser(DanelysFileParser):
    def __init__(self, journal, ftype="csv", **kwargs):
        super().__init__(journal, ftype=ftype, **kwargs)
        self.commission_field = "BILLINGFEES INCL. VAT"

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == "danelys_cb_csvparser"

    def _post(self, *args, **kwargs):
        super()._post(*args, **kwargs)
        final_rows = []
        for row in self.result_row_list:
            if not self.move_date or row["DATE"] > self.move_date:
                self.move_date = row.get("DATE")
            if row["EXECCODE"] in ("0", "0000"):
                final_rows.append(row)
        self.result_row_list = final_rows
