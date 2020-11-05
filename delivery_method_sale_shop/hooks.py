# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2015 Akretion (http://www.akretion.com).
#
##############################################################################
from openerp import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # keep test compatibility when delivery_method_sale_shop is installed with other modulel
    # that may have tests choosing a carrier already..
    # this could/should be drop if we may refactore as stated in todo file.
    main_shop = env['sale.shop'].search([], order='id asc', limit=1)
    if main_shop:
        carrier_accounts = env['keychain.account'].search([('namespace', 'ilike', 'roulier')])
        for account in carrier_accounts:
            carrier_type = account.namespace.split('roulier_')[-1]
            methods = env['delivery.carrier'].search([('carrier_type', 'ilike', carrier_type)])
            env['sale.shop.method'].create({
                'shop': main_shop.id,
                'delivery_methods': [(6, 0, methods.ids)],
                'keychain': account.id,
            })
        
