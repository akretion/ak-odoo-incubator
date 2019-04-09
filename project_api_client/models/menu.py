# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api
import logging
_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    def get_user_roots(self):
        """ Exclude 'Support' menu from displayed menu

        :return: the root menu ids
        :rtype: list(int)
        """
        res = super(IrUiMenu, self).get_user_roots()
        account = self.env['keychain.account'].sudo().retrieve(
            [('namespace', '=', 'support')])
        if not account:
            _logger.error('No keychain support key specify, hide the menu')
            support_imd = self.env.ref('project_api_client.external_project')
            menu_domain = [
                ('parent_id', '=', False), ('id', '!=', support_imd.id)]
            res = self.search(menu_domain)
        return res
