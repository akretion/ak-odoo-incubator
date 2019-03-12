# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


""" Mail parameters from odoo documentation:
     - ``mail_create_nosubscribe``: at create or message_post, do not subscribe
       uid to the record thread
     - ``mail_create_nolog``: at create, do not log the automatic '<Document>
       created' message
     - ``mail_notrack``: at create and write, do not perform the value tracking
"""

CTX = {
    'mail_create_nosubscribe': True,
    'mail_create_nolog': True,
    'mail_notrack': True,
}


class IrCron(models.Model):
    """ We want to be able to send custom messages in this object
        but we don't want, by default, automatic messages
        created by odoo core.
    """
    _name = 'ir.cron'
    _inherit = ['mail.thread']

    @api.model_create_multi
    def create(self, vals_list):
        return super(IrCron, self.with_context(CTX)).create(vals_list)

    def write(self, vals):
        return super(IrCron, self.with_context(CTX)).write(vals)
