# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import exceptions, fields, models

_logger = logging.getLogger(__name__)

# Use the generate_label from label2print.py in label_wizard then attach the Labels
# to the stock.picking


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "proxy.action.helper"]

    def print_product_label(self):
        self.ensure_one()
        return {
            "name": "Label wizard",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "label.from.record",
            "target": "new",
            "context": {"active_model": "stock.picking", "active_id": self.id}
        }

    def create_print_label_action_list(self, host, printer_name, labels):
        action_list = []
        for label in labels:
            action_list.append(
                self.get_print_data_action(
                    label.datas, printer_name=printer_name, raw=True, host=host
                )
            )
        return self.send_proxy(action_list)

    def print_receipt_report(self):
        self.ensure_one()
        printer_host = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("label_printer_poc.printer_host")
        )
        printer_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("label_printer_poc.a4_printer_name")
        )
        report = self.env.ref('stock.action_report_picking')
        result, _ = report.with_context(self.env.context)._render_qweb_pdf(self.id)
        return self.send_proxy([self.get_print_data_action(result, printer_name=printer_name, host=printer_host, raw=True)])


    def print_shipping_label(self):
        self.ensure_one()
        printer_host = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("label_printer_poc.printer_host")
        )
        printer_name = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("label_printer_poc.shipping_label_printer_name")
        )
        labels = self.env["shipping.label"].search(
            [
                ("res_model", "=", "stock.picking"),
                ("res_id", "=", self.id),
            ]
        )
        if not labels:
            self.send_to_shipper()
            labels = self.env["shipping.label"].search(
                [
                    ("res_model", "=", "stock.picking"),
                    ("res_id", "=", self.id),
                ]
            )
            if not labels:
                raise exceptions.UserError("No label found")

        return self.create_print_label_action_list(
                printer_host, printer_name, labels
        )

