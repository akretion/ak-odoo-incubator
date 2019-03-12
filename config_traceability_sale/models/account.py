# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields


""" Mail parameters from odoo documentation:
     - ``mail_create_nosubscribe``: at create or message_post, do not subscribe
       uid to the record thread
"""

CTX = {
    'mail_create_nosubscribe': True,
}


class AccountAccount(models.Model):
    """ We want to be able to send custom messages in this object
        but we don't want, by default, automatic messages
        created by odoo core.
    """
    _name = 'account.account'
    _inherit = ['account.account', 'mail.thread']

    name = fields.Char(track_visibility='onchange')
    reconcile = fields.Boolean(track_visibility='onchange')
    user_type_id = fields.Many2one(track_visibility='onchange')
    group_id = fields.Many2one(track_visibility='onchange')

    @api.model_create_multi
    def create(self, vals_list):
        return super(AccountAccount, self.with_context(CTX)).create(vals_list)

    def write(self, vals):
        return super(AccountAccount, self.with_context(CTX)).write(vals)
