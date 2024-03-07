# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from csv import QUOTE_MINIMAL, Dialect, register_dialect

from odoo.addons.account_move_base_import.parser.file_parser import (
    FileParser,
    float_or_zero,
)


class AdyenDialect(Dialect):
    delimiter = ","
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = "\n"
    quoting = QUOTE_MINIMAL


register_dialect("adyen_dialect", AdyenDialect)


class AdyenFileParser(FileParser):
    def __init__(self, journal, ftype="csv", **kwargs):
        conversion_dict = {
            "Payment Method": str,
            "Type": str,
            "Gross Debit (GC)": float_or_zero,
            "Gross Credit (GC)": float_or_zero,
            "Net Debit (NC)": float_or_zero,
            "Commission (NC)": float_or_zero,
            "Markup (NC)": float_or_zero,
            "Scheme Fees (NC)": float_or_zero,
            "Interchange (NC)": float_or_zero,
            "Merchant Reference": str,
        }
        super().__init__(
            journal,
            ftype=ftype,
            extra_fields=conversion_dict,
            dialect=AdyenDialect,
            **kwargs
        )
        self.commission_field = "Commission (NC)"

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == "adyen_cb_csvparser"

    def get_move_line_vals(self, line, *args, **kwargs):
        amount = line["Gross Credit (GC)"] or -line["Gross Debit (GC)"]
        res = {
            "name": line.get("Merchant Reference", ""),
            "credit": amount > 0.0 and amount or 0.0,
            "debit": amount < 0.0 and -amount or 0.0,
        }
        return res

    def _post(self, *args, **kwargs):
        res = super()._post(*args, **kwargs)
        # there are some fee line... not linked to a payment, we have to take it into
        # account
        self.extra_commission = 0.0
        final_rows = []
        for row in self.result_row_list:
            # account_move_import_base manage only once commission field when
            # adyen may have Commission (NC) with total commission or 3 fields with
            # detailed commission. => We fill the Commission (NC) in that case to have
            # a unique commission field
            if not row.get("Commission (NC)") and (
                row.get("Markup (NC)")
                or row.get("Scheme Fees (NC)")
                or row.get("Interchange (NC)")
            ):
                row["Commission (NC)"] = (
                    row["Markup (NC)"]
                    + row["Scheme Fees (NC)"]
                    + row["Interchange (NC)"]
                )
            if row.get("Type") in ("Settled", "Refunded", "SentForSettle"):
                final_rows.append(row)
            elif row["Type"] == "Fee":
                self.extra_commission += row["Net Debit (NC)"]
            create_date = row["Creation Date"].split(" ")[0]
            if not self.move_date or create_date > self.move_date:
                self.move_date = create_date
        self.result_row_list = final_rows
        return res


class AdyenPaypalParser(AdyenFileParser):
    def __init__(self, journal, ftype="csv", **kwargs):
        super().__init__(journal, ftype=ftype, **kwargs)
        self.support_multi_moves = True

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == "adyen_multi_move_csvparser"
