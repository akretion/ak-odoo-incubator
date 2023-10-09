import logging

from odoo import models

logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = "base"

    def _unknown_data_in_field(self, model, field, data_list, company_id=None):
        """Compare a data list with matching db data as specified model / field
        Example:
        model is "product.product"
        field is "default_code"
        data_list is ["FURN_7777", "ANY", "E-COM07", "E-COM08", "MISS-TEAK"]

        return missing data is ["ANY", "MISS-TEAK"]
        """

        def unique(my_list):
            return sorted(set(my_list))

        domain = [(field, "in", data_list)]
        if company_id:
            domain += [("company_id", "=", company_id)]
        data_list = unique(data_list)
        known_data = [x[field] for x in self.env[model].search(domain)]

        known_data = unique(known_data)
        unknown_data = [x for x in data_list if x not in known_data]
        if unknown_data:
            logger.info(
                f" >>> These data are not in this field {field} "
                f"in model {model} in db '{self.env.cr.dbname}'."
            )
        else:
            logger.info(
                f"Great! all provided data are present db {self.env.cr.dbname}."
            )
        return unknown_data
