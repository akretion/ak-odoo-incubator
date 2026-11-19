# @author Pierrick Brun <pierrick.brun@akretion.com>
# @author David Béal <david.beal@akretion.com>

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = [_name, "printable.mixin"]

    def _get_zebra_labels(self, data4print, content_params=None):
        """label_wizard module calls this method
        data4print content: tuple of product.product record, quantity
        if data4print is False then active_ids records are used.
            Check your label template placeholder match with these records
        """
        return self._get_labels_printer(data4print, content_params=content_params)

    def _get_raw_printer_label_template(self, content_params):
        """Override me in your own module and model.
        *** Required *** to generate printing
        """
        return ""

    def _get_printer_name(self):
        """Override me in your own module to set your specific name"""
        # TODO add parameter to choose printer name according some criterious
        return super()._get_printer_name()

    # Depecated method
    def get_labels_zebra(self, data4print, content_params=None):
        # TODO remove after 18.0
        _logger.warning(
            "Please call `_get_zebra_labels()` instead of `get_labels_zebra()`"
        )
        return self._get_zebra_labels(data4print, content_params=content_params)
