# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError

logger = logging.getLogger(__name__)


class ProductionRelease(models.Model):
    _name = "production.release"
    _description = "Production Release"
    _order = "name desc"

    name = fields.Char(string="Version", readonly=True)
    date = fields.Datetime(readonly=True)

    @api.model
    def _log_prod_release(self, crud_action):
        logger.warn(
            "User '%s' tried to %s 'production.release' record"
            % (self._uid, crud_action)
        )

    @api.multi
    def unlink(self):
        self._log_prod_release("unlink")
        res = super(ProductionRelease, self).unlink()
        raise UserError(
            _("Production Release can't be deleted from this database")
        )
        return res

    @api.multi
    def write(self, vals):
        self._log_prod_release("write")
        res = super(ProductionRelease, self).write(vals)
        raise UserError(
            _("Production Release can't be updated by manual entry")
        )
        return res
