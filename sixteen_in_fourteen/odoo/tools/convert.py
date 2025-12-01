# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo

from odoo.tools import convert

old_get_idref = convert._get_idref


def _get_idref(self, env, model_str, idref):
    rv = old_get_idref(self, env, model_str, idref)
    # Add Command to the eval context in data files
    rv["Command"] = odoo.fields.Command
    return rv


convert._get_idref = _get_idref
