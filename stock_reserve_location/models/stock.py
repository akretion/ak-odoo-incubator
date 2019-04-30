# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models

RESERVE_HELP = (
    "The location is used as reserve" " (opposite of picking location.)"
)


class StockLocation(models.Model):
    _inherit = "stock.location"

    reserve = fields.Boolean(string="Reserve", help=RESERVE_HELP)


class FixedPutawayStrat(models.Model):
    _inherit = "stock.product.putaway.strategy"

    reserve = fields.Boolean(
        string="Reserve",
        compute="_compute_reserve_location",
        store=True,
        help=RESERVE_HELP,
    )

    def _auto_init(self):
        """ idea from http://ludwiktrammer.github.io/odoo/
            changing-sql-constraints-child-models-odoo-8.html
        """
        self._sql_constraints = [
            (
                "putaway_product_unique",
                "unique(putaway_id,product_product_id,reserve)",
                _(
                    "Issue: Informations 'Putaway / Product / Reserve' combination "
                    "must be unique !\n\n"
                    "Action: Remove this location in the product storage locations."
                ),
            )
        ]
        super(FixedPutawayStrat, self)._auto_init()

    @api.multi
    @api.depends("fixed_location_id.reserve")
    def _compute_reserve_location(self):
        for rec in self:
            rec.reserve = rec.fixed_location_id.reserve


class ProductPutawayStrategy(models.Model):
    _inherit = "product.putaway"

    @api.model
    def _get_strategy_domain(self, putaway_strategy, product):
        domain = super(ProductPutawayStrategy, self)._get_strategy_domain(
            putaway_strategy, product
        )
        domain.append(("reserve", "=", False))
        return domain
