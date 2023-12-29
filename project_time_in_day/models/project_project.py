# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    def _get_hour_domain(self):
        return [
            ("category_id", "=", self.env.ref("uom.uom_categ_wtime").id),
            ("uom_type", "=", "smaller"),
        ]

    hour_uom_id = fields.Many2one(
        "uom.uom",
        "Hour Uom",
        help="Used for conversion between day and hours",
        domain=_get_hour_domain,
    )

    def _get_hour_uom(self):
        # By default in Odoo the uom of reference is the day
        # so depending of your location and multicompany case
        # you can have a different unit for hours (7h per day, 8h per day...)
        if self.hour_uom_id:
            return self.hour_uom_id
        else:
            return self.env.ref("uom.product_uom_hour")

    def convert_hours_to_days(self, value):
        return self._convert_to(value, "hours2days")

    def convert_days_to_hours(self, value):
        return self._convert_to(value, "days2hours")

    def _convert_to(self, value, conversion):
        uom_day = self.env.ref("uom.product_uom_day")
        uom_hour = self._get_hour_uom()
        if conversion == "days2hours":
            return uom_day._compute_quantity(value, uom_hour)
        elif conversion == "hours2days":
            return uom_hour._compute_quantity(value, uom_day)
