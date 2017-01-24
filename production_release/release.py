# coding: utf-8
# © 2017 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import _, models, fields
from openerp.exceptions import Warning as UserError


class ProductionRelease(models.Model):
    _name = 'production.release'
    _description = 'Production Release'

    name = fields.Char(string='Version', readonly=True)
    write_date = fields.Datetime(readonly=True)

    def unlink(self):
        raise UserError(
            _("Release can't be deleted"))
