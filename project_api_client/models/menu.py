# coding: utf-8
# © 2015 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models
from openerp.tools import config


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def get_user_roots(self, cr, uid, context=None):
        """ Return all root menu ids visible for the user.

        :return: the root menu ids
        :rtype: list(int)
        """
        res = super(IrUiMenu, self).get_user_roots(cr, uid, context=context)
        _, support_imd = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'project_api_client', 'external_project')
        # If this key is not there, we exclude the Support menu to avoid
        # connection with ERP master support
        if not config.get('keychain_key_prod'):
            menu_domain = [
                ('parent_id', '=', False), ('id', '!=', support_imd)]
            res = self.search(cr, uid, menu_domain, context=context)
        return res
