# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def run(self, procurements, raise_user_error=True):
        new_procurements = []
        for procurement in procurements:
            orderpoint = procurement.values.get("orderpoint_id")
            if (
                self.env.context.get("from_orderpoint")
                and orderpoint.location_destination_id
                and orderpoint.location_id == procurement.location_id
            ):
                new_procurements.append(
                    procurement._replace(location_id=orderpoint.location_destination_id)
                )
            else:
                new_procurements.append(procurement)
        return super().run(new_procurements, raise_user_error=raise_user_error)
