# -*- coding: utf-8 -*-
##############################################################################
#
#  licence AGPL version 3 or later
#  see licence in __openerp__.py or http://www.gnu.org/licenses/agpl-3.0.txt
#  Copyright (C) 2018 Akretion (http://www.akretion.com).
#
##############################################################################
from openerp import models, fields, api, exceptions, _
from openerp.fields import Date


class PurchaseLineExtractorWizard(models.TransientModel):
    _name = 'purchase.line.extractor.wizard'

    picking_type_id = fields.Many2one(
        'stock.picking.type', string='Deliver To')
    origin = fields.Char(readonly="True")
    date_order = fields.Date(default=Date.today())
    expected_date = fields.Date(default=Date.today())
    order_reference = fields.Char()
    line_ids = fields.One2many(
        'purchase.order.extract.line',
        'extractor_wizard_id',
        string='Purchase Lines')

    @api.multi
    def get_new_po_vals(self):
        self.ensure_one()
        vals = {
            'picking_type_id': self.picking_type_id.id,
            'origin': self.origin,
            'order_line': False,
            'open_order': False,
            'date_order': self.date_order,
        }
        if self.order_reference:
            vals['name'] = self.order_reference
        origin_po = self.line_ids[0].purchase_line_id.order_id
        # update location as picking type may have changed compared to open PO
        if not origin_po.dest_address_id and self.picking_type_id.default_location_dest_id:
            vals['location_id'] = self.picking_type_id.default_location_dest_id.id
        return vals

    @api.multi
    def check_open_order_state(self, orders):
        for po in orders:
            lines = po.order_line.filtered(lambda l: l.state != 'cancel')
            if all([line.product_qty == 0.0 for line in lines]):
                # We can close the order, as all qties have been extracted
                # And invoicing won't happen on this PO
                po.delete_workflow()
                po.write({'state': 'done'})

    @api.multi
    def extract_po_line(self):
        self.ensure_one()
        copy_po_vals = self.get_new_po_vals()
        new_po = self.line_ids[0].purchase_line_id.order_id.copy(copy_po_vals)
        extracted_po = self.env['purchase.order']
        for line in self.line_ids:
            if line.extract_quantity <= 0.0:
                continue
            purchase_line = line.purchase_line_id
            procs = purchase_line.procurement_ids
            move_dests = procs.mapped('move_dest_id')
            # Move this to write/create with open_order field?
            if move_dests:
                raise exceptions.Warning(
                    _('Extracting po line of purchase order coming from ' 
                      'make to order product is not possible.'))
            moves = purchase_line.move_ids.filtered(
                lambda m: m.state != 'cancel')
            if len(moves) != 1:
                raise exceptions.Warning(
                    _('Too much moves for product %s'
                      % purchase_line.product_id.default_code))
            extracted_po |= line.purchase_id
            line.generate_new_po_line(new_po, self.expected_date)
            line.update_quantity_extracted(moves)
        if not new_po.order_line:
            raise exceptions.Warning(
                _('No purchase line found'))
        new_po.signal_workflow('purchase_confirm')
        new_po.signal_workflow('purchase_approve')

        self.check_open_order_state(extracted_po)

        action = self.env.ref(
            'purchase.purchase_form_action')
        result = action.read()[0]
        view = self.env.ref('purchase.purchase_order_form')
        result['views'] = [(view.id, 'form')]
        result['res_id'] = new_po.id
        return result
