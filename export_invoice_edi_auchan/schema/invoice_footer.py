# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .base import SegmentInterface


class PIESegment(SegmentInterface):
    def get_values(self):
        return [
            (3, "PIE"),
            (10, self.invoice.amount_untaxed),  # Montant total hors taxes
            (10, self.invoice.amount_tax),  # Montant  taxes
            (10, self.invoice.amount_total),  # Montant total TTC
        ]
