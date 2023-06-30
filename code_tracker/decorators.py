# Copyright 2023 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import traceback
from functools import wraps

from odoo import fields

_logger = logging.getLogger(__name__)

# the decorator to know which function is called or not


def tracker_code(func):
    @wraps(func)
    def tracker_code_information(cls, *args, **kwargs):
        result = func(cls, *args, **kwargs)
        running_time = fields.Datetime.now()
        model_name = cls._name
        user = cls.env.user.name
        trace = ""
        trace_back = traceback.format_stack()
        for line in trace_back:
            trace += line
        trace_back_info = {}

        function_name = func.__name__
        trace_back_info = {
            "function_name": function_name,
            "model_name": model_name,
            "running_time": running_time,
            "user": user,
            "trace": trace,
        }
        cls.env["tracker.code.info"].create(trace_back_info)
        return result

    return tracker_code_information
