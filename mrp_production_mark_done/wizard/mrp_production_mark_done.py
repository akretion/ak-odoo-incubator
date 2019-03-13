# -*- coding: utf-8 -*-

from odoo import models, api, fields


class MrpProductionMarkDone(models.TransientModel):
    _name = 'mrp.production.mark.done'
    _description = "Mark Production as Done"

    item_ids = fields.One2many(
        'mrp.production.mark.done.item',
        'wiz_id', string='Manufacturing Orders')

    @api.multi
    def production_mark_done(self):
        for item in self.item_ids:
            production = item.production_id
            if production.state == 'confirmed':
                wizard_produce = self.env['mrp.product.produce'].create({
                    'production_id': production.id,
                    'product_id': production.product_id.id,
                    'product_qty': production.product_qty,
                })
                wizard_produce.do_produce()
            if production.state == 'progress':
                production.button_mark_done()
        return True

    @api.model
    def _prepare_item(self, production):
        return {
            'production_id': production.id,
            'name': production.name,
            'service_provider_id': production.service_provider_id.id,
            'service_id': production.service_id.id,
            'product_id': production.product_id.id,
            'product_qty': production.product_qty,
            'product_uom_id': production.product_uom_id.id,
            'state': production.state,
        }

    @api.model
    def default_get(self, fields):
        res = super(MrpProductionMarkDone, self).default_get(
            fields)
        production_obj = self.env['mrp.production']
        production_ids = self.env.context['active_ids'] or []
        if not production_ids:
            return res
        productions = []
        for production in production_obj.browse(production_ids):
            productions.append([0, 0, self._prepare_item(production)])
        res['item_ids'] = productions
        return res


class MrpProductionMarkDoneItem(models.TransientModel):
    _name = 'mrp.production.mark.done.item'
    _description = "Mark as Done from Production Item"

    wiz_id = fields.Many2one(
        'mrp.production.mark.done', string='Wizard', required=True,
        ondelete='cascade', readonly=True)
    production_id = fields.Many2one(string='Manufacturing Order',
                                    comodel_name='mrp.production',
                                    readonly=True)
    name = fields.Char(string='Reference')
    service_provider_id = fields.Many2one(string='Provider',
                                          comodel_name='res.partner')
    service_id = fields.Many2one(string='Service',
                                 comodel_name='product.product')
    product_id = fields.Many2one(string='Product',
                                 comodel_name='product.product')
    product_qty = fields.Float('Quantity To Produce')
    product_uom_id = fields.Many2one(string='Unit of Measure',
                                     comodel_name='product.uom')
    state = fields.Selection([
        ('confirmed', 'Confirmed'),
        ('planned', 'Planned'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State')
