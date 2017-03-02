# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Chafique Delli <chafique.delli@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import fields, models


class CrmCaseSection(models.Model):
    _inherit = 'crm.case.section'

    holding_company_id = fields.Many2one(
        'res.company', string='Holding Company for Invoicing',
        help="Select the holding company to invoice")
    holding_discount = fields.Float(string='Holding Discount (%)', default=0.0)
    holding_invoice_generated_by = fields.Selection([
        ('holding', 'Holding'),
        ('child', 'Child'),
        ], default='holding',
        string='Invoice Generated by',
        help="If the holding invoice is generated by a user of the holding "
             "company you have to select the option holding. If it's the "
             "child company you have to select the child option")
    holding_invoice_group_by = fields.Selection([
        ('none', 'None'),
        ('sale', 'Sale'),
        ], default='none',
        string='Invoice Group by',
        help="This will define how the sale order are grouped on the invoice")