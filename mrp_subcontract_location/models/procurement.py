# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# @author Florian da Costa <florian.dacosta@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models
import logging

_logger = logging.getLogger(__name__)


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    def _search_suitable_rule(self, domain):
        """ Return the right *StockMTO rule.

        We can have multiple Supplier: Inter Transit > StockMTO
        We want to get the rule with the right the next supplier
        """
        dest_partner = (
            self.move_dest_id[:1].procurement_id.warehouse_id.partner_id)
        res = False
        if dest_partner and self.route_ids:
            new_domain = (
                [('partner_address_id', '=', dest_partner.id)] +
                domain
            )
            res = super(ProcurementOrder, self)._search_suitable_rule(
                new_domain)
        if not res:
            res = super(ProcurementOrder, self)._search_suitable_rule(domain)
        return res
