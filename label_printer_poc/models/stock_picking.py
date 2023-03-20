# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import exceptions, fields, models

_logger = logging.getLogger(__name__)

# Put this in generic module with printer model so we configure it??? Worth it?
LABEL_ZEBRA_PRINTER = "zebra_large"
A4_PRINTER = "HP_LaserJet_400_M401d"

# Use the generate_label from label2print.py in label_wizard then attach the Labels
# to the stock.picking


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "proxy.action.helper"]

    def open_label_wizard(self):
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

    def create_label(self):
        self.ensure_one()
        attachment = self.env["ir.attachment"].search(
            [
                ("res_id", "=", self.id),
                ("res_model", "=", "stock.picking"),
                ("company_id", "=", self.company_id.id),
            ],
            order="create_date desc",
            limit=1,
        )
        self.env["shipping.label"].create(
            {
                "name": self.name + "label",
                "res_id": self.id,
                "res_model": "stock.picking",
                "datas": attachment.raw,
                "file_type": "pdf",
            }
        )

    def create_print_label_action_list(self, printer_name, labels):
        action_list = []
        for label in labels:
            action_list.append(
                self.get_print_data_action(
                    label.datas, printer_name=printer_name, raw=True
                )
            )
        return self.send_proxy(action_list)

    def print_label(self):
        self.ensure_one()
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

        return self.create_print_label_action_list(LABEL_ZEBRA_PRINTER, labels)
