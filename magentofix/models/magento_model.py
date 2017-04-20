# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.osv import orm
from openerp.addons.magentoerpconnect.product import ProductProductAdapter
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.magentoerpconnect.connector import get_environment
import logging
_logger = logging.getLogger(__name__)


class magento_backend(orm.Model):
    _inherit = 'magento.backend'

    def _check_stock_level(self, cr, uid, context=None):
        for backend_id in self.search(cr, uid, []):
            _logger.info('Start checking stock level')
            bind_obj = self.pool['magento.product.product']
            binding_ids = bind_obj.search(cr, uid, [
                ('backend_id', '=', backend_id)])
            bindings = bind_obj.browse(cr, uid, binding_ids)
            id2binding = {b.magento_id: b for b in bindings}
            session = ConnectorSession(cr, uid, context=context)
            env = get_environment(
                session, 'magento.product.product', backend_id)
            adapter = env.get_connector_unit(ProductProductAdapter)
            magento_ids = id2binding.keys()
            while magento_ids:
                process = magento_ids[:1000]
                magento_ids = magento_ids[1000:]
                res = adapter._call('product_stock.list', [process])
                for mag_product in res:
                    mag_qty = float(mag_product['qty'])
                    binding = id2binding[mag_product['product_id']]
                    odoo_qty = binding.magento_qty
                    if odoo_qty != mag_qty:
                        _logger.info(
                            'Wrong stock for product %s on magento,'
                            'should be %s got %s, fix it',
                            binding.default_code, odoo_qty, mag_qty)
                        binding.write({'magento_qty': binding.magento_qty})
