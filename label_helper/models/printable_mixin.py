# Copyright 2020 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging

from unidecode import unidecode

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PrintableMixin(models.AbstractModel):
    _name = "printable.mixin"
    _description = "Printable mixin methods"

    def _get_labels_printer(self, by_args=None, content_params=None, local=True):
        """send to client an action to print labels for products.

        products may be in self
        or in
        by_args may contain a list of (product.product, qty)
        """
        content_params = content_params or {}

        def update_content_params(record):
            """Update content_params with the record data."""
            content_params.update({"record": record})
            return content_params

        if not self and by_args:
            label_params = [
                {
                    "data": self._prepare_label_printer(update_content_params(record)),
                    "copies": qty or 1,
                }
                for record, qty in by_args
            ]
        else:
            label_params = [
                {"data": self._prepare_label_printer(content_params)} for record in self
            ]
        usage = self._get_printer_name()
        return self._print_labels(label_params, usage=usage, local=local)

    def _prepare_label_printer(self, content_params=None):
        tpl = self._get_raw_printer_label_template(content_params)
        if not tpl:
            raise UserError(
                _(
                    "No label template defined for this label.\nConsider to override "
                    + "_get_raw_printer_label_template() in your custom module"
                )
            )
        return base64.b64encode(tpl.encode("utf-8"))

    @api.model
    def _print_labels(self, label_params, usage, local=True):
        if local:
            printer = {"location": "https://localhost", "name": f"{usage}"}
        else:
            printer = self._get_network_printer_by_usage().get(usage)
        if not printer:
            raise UserError(_(f"No printer found for this usage '{usage}'"))
        _logger.debug(f"Printing something on {printer['name']}")
        action = {"host": printer["location"], "copies": 1}
        action["raw"] = True
        action["to_encode64"] = True
        action["printer_name"] = printer["name"]
        action["msg"] = (
            _(f"Sent to '{printer['name']}' printer")
            + self._get_printing_extra_message()
        )
        actions = []
        Proxy_m = self.env["proxy.action.helper"]
        for label in label_params:
            params = action.copy()
            params.update(label)
            actions.append(Proxy_m.get_print_data_action(**params))
        if actions:
            _logger.info(f"Sent to printer '{printer['name']}'")
        return Proxy_m.send_proxy(actions)

    def _get_printer_name(self):
        """Override me in your own module and adhoc model.
        *** Required *** to adapt to your devices
        """
        return "default"

    def _get_raw_printer_label_template(self, content_params):
        """Override me in your own module and model.
        just return a string
        """
        return ""

    def _goto_labelary(self, report_name, width, height, units="mm"):
        # You may call this method in your own module.
        params = get_content_params(self, report_name)
        url = "https://labelary.com/viewer.html?density=8&quality=grayscale&"
        size = f"width={width}&height={height}&units={units}"
        other = "&index=0&rotation=0&zpl="
        zpl = unidecode(params[0].get("data").decode("utf8").replace("\n", "%0A"))
        return {
            "type": "ir.actions.act_url",
            "url": f"{url}{size}{other}{zpl}",
            "target": "new",
        }

    def _get_printing_extra_message(self):
        """Override me
        Extra message is displayed in the popup window when printing.
        """
        return ""

    def _get_network_printer_by_usage(self):
        """Override in your own model"""
        # Technical info don't need translation
        message = """
You may just implement `_get_network_printer_by_usage()` in your targeted model
to define which one use or have a look to this module:
https://github.com/OCA/report-print-send/blob/16.0/printing_simple_configuration/models/printer.py#L34
"""  # noqa E501
        _logger.info(
            _(
                "Non local printers needs rules to be routed to the right device.\n"
                + "Contact your integrator for more information"
            )
            + message
        )
        return {}


def get_content_params(self, report_str):
    # We get data content from report
    data = self.env["ir.actions.report"]._render_qweb_text(
        self.env.ref(report_str), self.env.context.get("active_ids")
    )[0]
    return [{"data": data, "copies": 1}]
