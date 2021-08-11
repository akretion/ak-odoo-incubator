# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _make_po_get_domain(self, company_id, values, partner):
        domain = super()._make_po_get_domain(company_id, values, partner)
        orderpoint = values.get("orderpoint_id", False)
        dest_location = orderpoint.location_destination_id.id or False
        domain += (("specific_location_id", "=", dest_location),)
        return domain

    def _prepare_purchase_order(self, company_id, origins, values):
        vals = super()._prepare_purchase_order(company_id, origins, values)
        values = values[0]
        orderpoint = values.get("orderpoint_id", False)
        vals["specific_location_id"] = orderpoint.location_destination_id.id or False
        return vals
