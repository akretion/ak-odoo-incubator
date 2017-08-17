# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models

PRICELIST_HELP = """
- "Use Market Pricelist": This option force pricelist
  to the market pricelist defined on this sale team'
- "Force Partner Pricelist": This option force pricelist
  to the partner pricelist'
- "Use Partner Pricelist if not public": This option allow to use
   partner pricelist if it's not public. Otherwise we use
   to the market pricelist defined on this sale team.
   If this field is not set we use default behavior.
"""


class CrmCaseSection(models.Model):
        _inherit = "crm.case.section"

        pricelist_id = fields.Many2one(
            comodel_name='product.pricelist',
            string="Pricelist",
            company_dependent=True)
        price_policy = fields.Selection(
            selection=[('contract_pricelist', 'Force Market Pricelist'),
                       ('partner_pricelist', 'Force Partner Pricelist'),
                       ('partner_pricelist_if_not_default',
                        'Use Partner Pricelist if not public'),
                       ],
            help=PRICELIST_HELP)
