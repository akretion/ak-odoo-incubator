# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, registry

# TODO use _register_hook() instead of this hack to code an independant module


if 'account' in registry()._init_modules:
    class AccountInvoice(models.Model):
        _inherit = ['account.invoice', 'forbidden.model']
        _name = 'account.invoice'


if 'sale' in registry()._init_modules:
    class SaleOrder(models.Model):
        _inherit = ['sale.order', 'forbidden.model']
        _name = 'sale.order'


if 'purchase' in registry()._init_modules:
    class PurchaseOrder(models.Model):
        _inherit = ['purchase.order', 'forbidden.model']
        _name = 'purchase.order'


if 'stock' in registry()._init_modules:
    class StockPicking(models.Model):
        _inherit = ['stock.picking', 'forbidden.model']
        _name = 'stock.picking'


if 'mrp' in registry()._init_modules:
    class MrpProduction(models.Model):
        _inherit = ['mrp.production', 'forbidden.model']
        _name = 'mrp.production'


if 'point_of_sale' in registry()._init_modules:
    class PosOrder(models.Model):
        _inherit = ['pos.order', 'forbidden.model']
        _name = 'pos.order'
