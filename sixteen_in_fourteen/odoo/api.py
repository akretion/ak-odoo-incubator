# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.api import Environment


def flush_all(self):
    # This is not a 1:1 backport of the 16.0 method, a lot has changed
    # but it should hopefully be enough.
    # See: https://github.com/odoo/odoo/pull/87527

    self["base"].flush()


Environment.flush_all = flush_all
