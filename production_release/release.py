# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, api, models, fields
from openerp.exceptions import Warning as UserError

import logging
logger = logging.getLogger(__name__)


class ProductionRelease(models.Model):
    _name = 'production.release'
    _description = 'Production Release'

    name = fields.Char(string='Version', readonly=True)
    date = fields.Datetime(readonly=True)

    @api.model
    def _log_prod_release(self, crud_action):
        logger.warn(
            "User '%s' tried to %s 'production.release' record" % (
                self._uid, crud_action))

    @api.multi
    def unlink(self):
        self._log_prod_release('unlink')
        raise UserError(
            _("Production Release can't be deleted from this database"))

    @api.multi
    def write(self, vals):
        self._log_prod_release('write')
        raise UserError(
            _("Production Release can't be updated by manual entry"))
