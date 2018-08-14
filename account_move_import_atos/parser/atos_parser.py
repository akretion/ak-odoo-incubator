# -*- coding: utf-8 -*-
# Copyright 2012-2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools.translate import _
import datetime
from odoo.addons.account_move_base_import.parser.file_parser import FileParser
from csv import Dialect
from _csv import QUOTE_MINIMAL, register_dialect
from odoo.osv import osv


def float_or_zero(val):
    """ Conversion function used to manage
    empty string into float usecase"""
    val = val.strip()
    return (float(val.replace(',', '.')) if val else 0.0) / 100.


def format_date(val):
    return datetime.datetime.strptime(val, "%Y%m%d")


class atos_dialect(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = '\t'
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = '\n'
    quoting = QUOTE_MINIMAL


register_dialect("atos_dialect", atos_dialect)


class AtosFileParser(FileParser):

    def __init__(self, journal, ftype='csv', **kwargs):
        extra_fields = {
            "OPERATION_DATE": format_date,
            "PAYMENT_DATE": unicode,
            "TRANSACTION_ID": unicode,
            "OPERATION_NAME": unicode,
            "OPERATION_AMOUNT": float_or_zero,
        }
        self.refund_amount = None
        super(AtosFileParser, self).__init__(
            journal, ftype=ftype,
            extra_fields=extra_fields,
            dialect=atos_dialect, **kwargs)

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_move_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == 'atos_csvparser'

    def _pre(self, *args, **kwargs):
        split_file = self.filebuffer.split("\n")
        selected_lines = []
        for line in split_file:
            if line.startswith("FIN"):
                break
            selected_lines.append(line.strip())
        self.filebuffer = "\n".join(selected_lines)

    def _parse(self, *args, **kwargs):
        # return super(AtosFileParser, self)._parse(*args, **kwargs)
        self.result_row_list = self._parse_csv()
        return True

    def get_move_line_vals(self, line, *args, **kwargs):
        """
        This method must return a dict of vals that can be passed to create
        method of statement line in order to record it. It is the
        responsibility of every parser to give this dict of vals, so each one
        can implement his own way of recording the lines.
            :param:  line: a dict of vals that represent a line of
              result_row_list
            :return: dict of values to give to the create method of statement
              line, it MUST contain at least:
                {
                    'name':value,
                    'date_maturity':value,
                    'credit':value,
                    'debit':value
                }
        """
        amount = line['OPERATION_AMOUNT']
        credit = bool(line['OPERATION_NAME'] == 'CREDIT_CAPTURE')
        res = {
            'name': line["OPERATION_NAME"] + '_' + line["TRANSACTION_ID"],
            'date_maturity': line["OPERATION_DATE"],
            'credit': amount if credit else 0.0,
            'debit': amount if not credit else 0.0,
            # 'transaction_id': line["PAYMENT_DATE"] + line["TRANSACTION_ID"],
        }
        return res

    def _post(self, *args, **kwargs):
        """
        Compute the total transfer amount
        """
        res = super(AtosFileParser, self)._post(*args, **kwargs)
        self.transfer_amount = 0.0
        self.refund_amount = 0.0
        rows = []
        for row in self.result_row_list:
            if row['OPERATION_NAME'] in ('CREDIT'):
                continue
            rows.append(row)
            if row['OPERATION_NAME'] == 'CREDIT_CAPTURE':
                row["OPERATION_AMOUNT"] = - row["OPERATION_AMOUNT"]
                self.refund_amount -= row["OPERATION_AMOUNT"]
            elif row['OPERATION_NAME'] == 'DEBIT_CAPTURE':
                self.transfer_amount -= row["OPERATION_AMOUNT"]
            else:
                raise osv.except_osv(
                    _("User Error"),
                    _("The bank statement imported have invalide line,"
                      " indeed the operation type %s is not supported")
                    % row['OPERATION_NAME'])
        self.result_row_list = rows
        self.statement_date = self.result_row_list[0]["OPERATION_DATE"]
        return res

    # def get_refund_amount(self):
    #     return self.refund_amount
