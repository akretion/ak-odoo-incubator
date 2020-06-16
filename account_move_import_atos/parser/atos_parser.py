# -*- coding: utf-8 -*-
# Copyright 2012-2018 Akretion (http://www.akretion.com).
# @author Benoît GUILLOT <benoit.guillot@akretion.com>
# @author Pierrick BRUN <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime
from csv import Dialect

from odoo.addons.account_move_base_import.parser.file_parser import FileParser
from odoo.tools.translate import _

# pylint: disable=W7935,W7936
from _csv import QUOTE_MINIMAL, register_dialect


def float_or_zero(val):
    """ Conversion function used to manage
    empty string into float usecase"""
    val = val.strip()
    return (float(val.replace(",", ".")) if val else 0.0) / 100.0


def format_date(val):
    return datetime.datetime.strptime(val, "%Y-%m-%d %H:%M:%S")


class AtosDialect(Dialect):
    """Describe the usual properties of Excel-generated CSV files."""

    delimiter = "\t"
    quotechar = '"'
    doublequote = False
    skipinitialspace = False
    lineterminator = "\n"
    quoting = QUOTE_MINIMAL


register_dialect("atos_dialect", AtosDialect)


class AtosFileParser(FileParser):
    def __init__(self, journal, ftype="csv", **kwargs):
        extra_fields = {
            "operationDateTime": format_date,
            "transactionReference": unicode,
            "operationAmount": float_or_zero,
        }
        self.refund_amount = None
        super(AtosFileParser, self).__init__(
            journal,
            ftype=ftype,
            extra_fields=extra_fields,
            dialect=AtosDialect,
            **kwargs
        )

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_move_parser class factory. Return true if
        the providen name is generic_csvxls_so
        """
        return parser_name == "atos_csvparser"

    def _pre(self, *args, **kwargs):
        split_file = self.filebuffer.split("\n")
        split_file.pop(0)  # first line is the title
        selected_lines = []
        for line in split_file:
            if line.startswith("END"):
                break
            selected_lines.append(line.strip())
        self.filebuffer = "\n".join(selected_lines)

    def _parse(self, *args, **kwargs):
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
        amount = line["operationAmount"]
        operation_names = ["CREDIT_CAPTURE", "DEBIT_CAPTURE", "CREDIT"]
        if line["operationName"] not in operation_names:
            raise Exception(
                _(
                    "The bank statement imported has invalid line(s),"
                    " the operation type %s is not supported"
                    % line["operationName"]
                )
            )

        # inversed because the file is written from the bank's point of view,
        # a credit in the file is then a debit from odoo's side
        is_credit = bool(line["operationName"] == "DEBIT_CAPTURE")
        res = {
            "name": line["operationName"] + "_" + line["transactionReference"],
            "date_maturity": line["operationDateTime"],
            "credit": amount if is_credit else 0.0,
            "debit": amount if not is_credit else 0.0,
            "transaction_ref": line["transactionReference"],
        }
        return res
