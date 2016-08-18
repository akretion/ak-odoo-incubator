# coding: utf-8
# © 2016 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp import SUPERUSER_ID


class IrCron(models.Model):
    _inherit = 'ir.cron'

    active_old = fields.Boolean(
        string='Intial active state',
        help="State of the cron before 'Active Previous Active Cron' "
             "module installation.")


class Module(models.Model):
    _inherit = 'ir.module.module'

    def init(self, cr):
        cron_m = self.pool['ir.cron']
        cron_ids = cron_m.search(cr, SUPERUSER_ID, [])
        if cron_ids:
            vals = {'active': False, 'active_old': True}
            cron_m.browse(cr, SUPERUSER_ID, cron_ids).write(vals)

    def button_uninstall(self, cr, uid, ids, context=None):
        cron_m = self.pool['ir.cron']
        context.update({'active_test': False})
        cron_ids = cron_m.search(
            cr, uid, [('active_old', '=', True)], context=context)
        if cron_ids:
            vals = {'active': True}
            cron_m.browse(cr, uid, cron_ids).write(vals)
        return super(Module, self).button_uninstall(
            cr, uid, ids, context=context)
