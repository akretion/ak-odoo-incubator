# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _


PURCHASE_STATES = [
    ('draft', 'RFQ'),
    ('sent', 'RFQ Sent'),
    ('po_sent', 'PO Sent'),
    ('to approve', 'To Approve'),
    ('purchase', 'Purchase Order'),
    ('done', 'Locked'),
    ('cancel', 'Cancelled')
]

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Do not use selection_add because the order is important, we do not
    # want the po_sent at the end
    state = fields.Selection(selection=PURCHASE_STATES)
