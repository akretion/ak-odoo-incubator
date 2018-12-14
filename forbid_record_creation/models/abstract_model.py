# © 2019 Akretion Mourad EL HADJ MIMOUNE, David BEAL, Raphaël REVERDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, _
from odoo.exceptions import UserError


# TODO use _register_hook() instead of this hack to code an independant module


class ForbiddenModel(models.AbstractModel):
    _name = 'forbidden.model'
    _description = 'Prevent order creation'

    @api.model
    def _my_integrator(self):
        """ Override with your own brand"""
        return 'Akretion'

    @api.model
    def _prevent_orders(self):
        """ You may inherit this method according to 'web.base.url' like here
            url = self.env['ir.config_parameter'].get_param('web.base.url')
            if url[-19:] == '/my_test_instance.com':
                return False
        """
        return True

    @api.model
    def create(self, vals):
        if self._prevent_orders():
            raise UserError(
                _("You're not allowed to create '%s' on this database.\n\n"
                  "Your integrator, %s"
                  % (self._description, self._my_integrator())))
        return super().create(vals)
