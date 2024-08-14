# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .base import SegmentInterface


class LIGSegment(SegmentInterface):
    def get_values(self):
        uom = (
            self.line.product_uom_id.name == "kg"
            and "KGM"
            or self.line.product_uom_id.name == "m"
            and "MTR"
            or "PCE"
        )

        return [
            (3, "LIG"),
            (
                6,
                self.line_num,
            ),  # Numéro de ligne (de 1 à n remis à 0 pour chaque facture)
            (14, self.line.product_id.barcode),  # Code EAN produit
            (
                35,
                self.line.product_id.default_code,
            ),  # Code interne produit chez le fournisseur
            (
                10,
                self.line.sale_line_ids
                and self.line.sale_line_ids[0].product_packaging_id.qty
                or 1,
            ),  # Par combien
            # (multiple de commande)
            (
                10,
                self.line.sale_line_ids
                and self.line.sale_line_ids[0].product_uom_qty
                or self.line.quantity,
            ),
            # Quantité commandée
            (3, uom),  # Unité de quantité (PCE = pièce, KGM = kilogramme, MTR = mètre)
            (10, self.line.quantity),  # Quantité facturée
            (15, self.line.price_unit),  # Prix unitaire net
            (3, self.line.move_id.currency_id.name),  # Code monnaie (EUR = euro)
            (1, "", False),
            (1, "", False),
            (5, self.line.tax_ids and self.line.tax_ids[0].amount or 0),
            (
                15,
                self.line.quantity
                and (self.line.price_total / self.line.quantity)
                or 0.0,
            ),  # Prix unitaire brut
            (1, "", False),
            (70, self.line.name, {"truncate_silent": True}),
            (17, self.line.price_subtotal),  # Montant Net Ht de la ligne
        ]
