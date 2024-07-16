# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import math

from odoo import api, fields, models

STD_PALLET_VOLUME = 1650 * 800 * 1200


class PalletFillingMixin(models.AbstractModel):

    _name = "pallet.filling.mixin"
    _description = "Pallet Filling Mixin"  # TODO

    pallet_estimation = fields.Integer(
        string="Nombre de palettes estimées",
        help="Estimation du nombre de palettes pour cette commande",
        compute="_compute_pallet_estimation",
        store=False,
    )
    pallet_estimation_warning = fields.Char(
        string="Avertissement",
        compute="_compute_pallet_estimation",
        store=False,
    )

    @api.model
    def _get_pallet_filling_constants(self):
        return STD_PALLET_VOLUME, 75

    def _get_pkgs_total_volume(self, lines):
        total_volume = 0
        for line in lines:
            pkg_nbr = math.ceil(line.product_uom_qty / line.product_packaging_id.qty)
            total_volume += pkg_nbr * line.product_packaging_id.package_type_id.volume
        return total_volume

    def _pallet_filling_calc(self):  # TODO optimize perf ?
        lines = self[self._pallet_line_fieldname]
        lines_without_packaging = lines.filtered(
            lambda r: not r.product_packaging_id.package_type_id
            or not r.product_packaging_id
        )
        if lines_without_packaging:
            warning = (
                f"Les articles suivants n'ont pas de"
                f" colisage pour calcul du remplissage "
                f"de palette: "
                f"{lines_without_packaging.mapped('product_id.default_code')}"
            )
        else:
            warning = ""
        lines_with_packaging = lines - lines_without_packaging
        pallet_volume, filling_rate = self._get_pallet_filling_constants()
        pallet_estimation = math.ceil(
            self._get_pkgs_total_volume(lines_with_packaging)
            / (pallet_volume * (filling_rate / 100))
        )
        return pallet_estimation, warning

    def _compute_pallet_estimation(self):
        for rec in self:
            (
                rec.pallet_estimation,
                rec.pallet_estimation_warning,
            ) = rec._pallet_filling_calc()

    @property
    def _pallet_line_fieldname(self):
        raise NotImplementedError
