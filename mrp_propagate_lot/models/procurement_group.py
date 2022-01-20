# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def _get_custom_lot_vals(self, origin_lot, product, idx, procurement=None):
        vals = origin_lot.copy_data()[0]
        vals.update(
            {
                "name": "%s-%d" % (vals["name"], idx),
                "product_id": product.id,
                "phantom_lot_id": origin_lot.id,
            }
        )
        return vals

    @api.model
    def _get_kit_component_procurements(self, procurements):
        procurements = super()._get_kit_component_procurements(procurements)
        # in case we had a restrict lot, the procurements were splitted and product
        # changed but not the lot. if components are tracked by lot, we whould
        # duplicate the original phantom lot to change the product
        lot_obj = self.env["stock.production.lot"]
        new_procurements = []
        index_per_lot = {}
        for procurement in procurements:
            restrict_lot_id = procurement.values.get("restrict_lot_id", False)
            lot = lot_obj.browse(restrict_lot_id)
            product = procurement.product_id
            if lot and lot.product_id != product:
                if product.auto_generate_prodlot:
                    if lot.id not in index_per_lot:
                        index_per_lot[lot.id] = 0
                    index_per_lot[lot.id] += 1
                    vals = self._get_custom_lot_vals(
                        lot, product, index_per_lot[lot.id], procurement=procurement
                    )
                    new_lot_id = lot_obj.create(vals).id
                else:
                    new_lot_id = False
                new_values = procurement.values.copy()
                new_values["restrict_lot_id"] = new_lot_id
                new_procurements.append(procurement._replace(values=new_values))
            else:
                new_procurements.append(procurement)
        return new_procurements
