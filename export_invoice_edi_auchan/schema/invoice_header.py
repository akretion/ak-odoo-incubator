# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from .base import SegmentInterface


class ENTSegment(SegmentInterface):
    def get_values(self):
        return [
            (3, "ENT"),  # Étiquette de segment "ENT"
            (70, self.invoice.invoice_origin),  # Numéro de commande du client
            (
                10,
                self.source_orders and self.source_orders[0].date_order or "",
            ),  # Date de commande JJ/MM/AAAA
            (5, "", False),  # Heure de commande HH:MN opt
            (10, "", False),  # date du message opt
            (5, "", False),  # Heure du message opt
            (
                10,
                self.bl_date,
            ),  # Date du BL JJ/MM/AAAA
            (
                35,
                self.bl_nbr,
            ),  # num du BL JJ/MM/AAAA
            (10, "", False),  # Date avis d'expédition JJ/MM/AAAA  opt
            (35, "", False),  # Numéro de l'avis d'expédition  opt
            (10, "", False),  # Date d'enlèvement JJ/MM/AAAA opt
            (5, "", False),  # Heure d'enlèvement HH:MN opt
            (35, self.invoice.name),  # Numéro de document
            (
                16,
                self.invoice.invoice_date,
            ),  # Date/heure facture ou avoir (document) JJ/MM/AAAA HH:MN
            (10, self.invoice.invoice_date_due),  # Date d'échéance JJ/MM/AAAA
            (
                7,
                self.invoice.move_type == "out_invoice"
                and "Facture"
                or (self.invoice.move_type == "out_refund" and "Avoir")
                or "",
            ),  # Type de document (Facture/Avoir)
            # depend on  'move_type', 'in', ('out_invoice', 'out_refund')
            (3, self.invoice.currency_id.name),  # Code monnaie (EUR pour Euro)
            (10, "", False),  # Date d'échéance pour l'escompte JJ/MM/AAAA  opt
            (
                10,
                "",
                False,
            ),  # Montant de l'escompte (le pourcentage de l'escompte est préconisé) opt
            (
                35,
                "",
                False,
            ),  # Numéro de facture en référence (obligatoire si avoir) opt
            (10, "", False),  # Date de facture en référence (obligatoire si avoir) opt
            (6, "", False),  # Pourcentage de l'escompte opt
            (3, "", False),  # Nb de jour de l'escompte opt
            (6, "", False),  # Pourcentage de pénalité opt
            (3, "", False),  # Nb de jour de pénalité opt
            (
                1,
                self.invoice.env.context.get("test_mode") and "1" or "0",
            ),  # Document de test (1/0)
            (
                3,
                "42",
            ),  # Code paiement (cf table ENT.27) 42 ==> Paiement à un compte
            # bancaire (virement  client)
            # fix ==> rendre ce champs dynamique ?
            (3, "MAR"),  # Nature document (MAR pour marchandise et SRV pour service)
            # fix ==> rendre ce champs dynamique ?
        ]
