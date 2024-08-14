# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import datetime

import freezegun
from unidecode import unidecode

from odoo.tools import float_compare


class SegmentInterfaceExc(Exception):
    pass


class SegmentInterface:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def _format_values(self, size, value="", required=True, ctx=False):
        if required and (value is False or value is None or value == ""):
            raise ValueError()
        if not ctx:
            ctx = {}
        if not value:
            value = ""
        if isinstance(value, freezegun.api.FakeDate):
            fmt_val = datetime.date.strftime(value, "%d/%m/%Y")
        elif isinstance(value, datetime.datetime):
            fmt_val = datetime.date.strftime(value.date(), "%d/%m/%Y %H:%M")
        elif isinstance(value, int):
            fmt_val = str(value)
        elif isinstance(value, float):
            if float_compare(value, 0, 3) == 0 and ctx.get("empty_if_zero"):
                fmt_val = ""
            else:
                if ctx.get("decimal_3"):
                    fmt_val = str("{:.3f}".format(value))
                else:
                    fmt_val = str("{:.2f}".format(value))
        elif isinstance(value, str):
            fmt_val = unidecode(value)
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
        if len(fmt_val) > size:
            if ctx.get("truncate_silent"):
                fmt_val = fmt_val[:size]
            else:
                errorstr = "{} trop long, taille maximale est de {}".format(
                    fmt_val, size
                )
                if ctx:
                    errorstr = "contexte: {}".format(ctx) + errorstr
                raise ValueError(errorstr)
        return fmt_val

    def render(self):
        res = ""
        errors = []
        for idx, fmt_data in enumerate(self.get_values(), start=1):
            try:
                fmt_val = self._format_values(*fmt_data)
                res += fmt_val + ";"
            except ValueError:
                errors += [(self.__class__.__name__, idx)]
        if errors:
            errstr = ""
            for el in errors:
                errstr += f"Segment {el[0]}: missing value on line {el[1]}\n"
            raise SegmentInterfaceExc(errstr)
        return res[:-1]

    def get_values(self):
        raise NotImplementedError
