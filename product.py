# -*- coding: utf-8 -*-

from openerp import api, fields, models

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'
    print "je suis la"
    product_id = fields.Many2one('product.product', string='Product Variant', help="When this field is filled in, the vendor data will only apply to the variant.")

class ProductProduct(models.Model):
    _inherit = 'product.product'

    print "product product"

    seller_ids = fields.Many2many('product.supplierinfo', compute='_compute_seller_ids')
    seller_delay = fields.Integer(related='seller_ids.delay', string='Supplier Lead Time',
                                help="This is the average delay in days between the purchase order confirmation and the receipts for this product and for the default supplier. It is used by the scheduler to order requests based on reordering delays.")
    seller_qty = fields.Float(related='seller_ids.qty', string='Supplier Quantity',
                                        help="This is minimum quantity to purchase from Main Supplier.")
    seller_id  = fields.Many2one(related='seller_ids.name', relation='res.partner', string='Main Supplier',
                                                help="Main Supplier who has highest priority in Supplier List.")


    def _compute_seller_ids(self):
        for product in self:
            print "Pour le produit", product.name, "id: ", product.id, "tmpl: ", product.product_tmpl_id
            product_supplier_specific = self.env['product.supplierinfo'].browse(False)
            product_supplier_generic  = self.env['product.supplierinfo'].browse(False)
            for supplierinfo in product.product_tmpl_id.seller_ids:
                print "  ", supplierinfo.id,  " seq: ",supplierinfo.sequence,  supplierinfo.name.name," id:", supplierinfo.product_id, "tmpl: ", supplierinfo.product_tmpl_id
                if not supplierinfo.product_id:
                    product_supplier_generic |= supplierinfo
                    print "on garde un generic"
                elif supplierinfo.product_id == product:
                    product_supplier_specific |= supplierinfo
                    print "on garde un specific"
                else:
                    print "on garde pas"
            product.seller_ids = product_supplier_specific + product_supplier_generic
            print "result", product.seller_ids


