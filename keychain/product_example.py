# -*- coding: utf-8 -*-
# © 2016 Akretion Mourad EL HADJ MIMOUNE, David BEAL, Raphaël REVERDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields
import logging

_logger = logging.getLogger(__name__)


class AccountProduct(models.Model):
    _inherit = 'keychain.account'

    namespace = fields.Selection(
        selection_add=[('roulier_laposte', 'Laposte')])

    def _roulier_laposte_init_data(self):
        print "laposte"
        return {
            "codeAgence": "",
            "bim": "boum"
        }

    def _roulier_laposte_validate_data(self, data):
        print "on valide data"
        # on aurait pu utiliser Cerberus ici
        return 'codeAgence' in data


#class LaposteProduct(models.Model):
#   _inherit = 'product.product'
#   account = fields.Many2one(
#       'keychain.account',
#       string="Lien vers compte",
#       help="Lien vers un keychain")
