# -*- coding: utf-8 -*-
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

from openerp.addons.account_statement_base_import.parser.file_parser import (
    FileParser
)
from openerp.addons.account_statement_base_import.parser.generic_file_parser import (
    float_or_zero,
)
    
from csv import Dialect
from _csv import QUOTE_MINIMAL, register_dialect


class payplug_dialect(Dialect):
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = QUOTE_MINIMAL


register_dialect("payplug_dialect", payplug_dialect)


class PayplugFileParser(FileParser):
    def __init__(self, parse_name, ftype='csv'):
        conversion_dict = {
            'Montant': float_or_zero,
            'Date': unicode,
            'ID API': unicode,
            'Description': unicode,
            'E-mail': unicode,
        }
        super(PayplugFileParser, self).__init__(
            parse_name, ftype=ftype, conversion_dict=conversion_dict,
            dialect=payplug_dialect
        )

    @classmethod
    def parser_for(cls, parser_name):
        """
        Used by the new_bank_statement_parser class factory. Return true if
        the providen name is be2bill_csvparser
        """
        return parser_name == 'payplug_csvparser'

    def _pre(self, *args, **kwargs):
        super(PayplugFileParser, self)._pre(*args, **kwargs)
        split_file = self.filebuffer.split("\n")
        selected_lines = []
        for line in split_file:
            if line.startswith('sep'):
                continue
            selected_lines.append(line.strip())
        self.filebuffer = "\n".join(selected_lines)

    def get_st_line_vals(self, line, *args, **kwargs):
        if line['ID API'].startswith('re'):
            transaction_ref = ''
            ref = line['ID API'] + ' %s' % line.get('E-mail')
        else:
            ref = line['ID API'] or line['Description']
            transaction_ref = line['ID API']
        res = {
            'transaction_id': transaction_ref,
            'name': ref,
            'date': line['Date'],
            'amount': line['Montant'],
            'ref': ref,
        }
        return res

    def _post(self, *args, **kwargs):
        super(PayplugFileParser, self)._post(*args, **kwargs)
        for row in self.result_row_list:
            if row['Date'] > self.statement_date:
                self.statement_date = row['Date']
