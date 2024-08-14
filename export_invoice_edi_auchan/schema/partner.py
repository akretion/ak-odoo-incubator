# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .base import SegmentInterface


class PARSegment(SegmentInterface):
    def get_values(self):
        return [
            (3, "PAR"),
            (13, self.invoice.partner_shipping_id.barcode),  # Code EAN client
            (35, self.invoice.partner_shipping_id.name, False),  # Libellé client
            (
                13,
                self.invoice.company_id.partner_id.barcode,
            ),  # Code EAN Fournisseur (vendeur)
            (
                35,
                self.invoice.company_id.partner_id.name,
                False,
            ),  # Libellé Fournisseur (vendeur)
            (13, self.invoice.partner_shipping_id.barcode),  # Code EAN client livré
            (35, self.invoice.partner_shipping_id.name, False),  # Libellé client livré
            (13, self.invoice.partner_id.barcode),  # Code EAN client facturé à
            (35, self.invoice.partner_id.name, False),  # Libellé client facturé à
            (10, "", False),  # Code EAN factor (obligatoire si factor)
            (10, "", False),  # Libellé alias factor (obligatoire si factor)
            (13, self.invoice.company_id.partner_id.barcode),  # Code EAN régler à
            (35, self.invoice.company_id.partner_id.name, False),  # Libellé régler à
        ]
