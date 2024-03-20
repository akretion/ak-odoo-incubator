# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .base import SegmentInterface


class TVASegment(SegmentInterface):
    def get_values(self):

        return [
            (3, "TVA"),  # Étiquette de segment "TVA"
            (5, self.tax_line.tax_line_id.amount),  # Heure de commande HH:MN opt
            (10, self.tax_line.tax_base_amount),  # Heure de commande HH:MN opt
            (10, self.tax_line.price_subtotal),  # Heure de commande HH:MN opt
        ]
