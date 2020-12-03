# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

import simplejson

from odoo import fields, models


class ProductConfigurationMixin(models.AbstractModel):
    _name = "product.configuration.mixin"
    _description = "Mixin to manage commercial and technical configuration"

    def _compute_configuration(self):
        for line in self:
            line.config_text = simplejson.dumps(line.config)

    def _inverse_configuration(self):
        for line in self:
            if line.config_text:
                line.config = simplejson.loads(self.config_text)

    config = fields.Serialized(
        "Json Configuration", readonly=False, help="Allow to set custom configuration"
    )
    config_text = fields.Text(
        compute="_compute_configuration",
        inverse="_inverse_configuration",
        string="Configuration",
    )
    commercial_config = fields.Serialized(
        "Json Commercial Configuration", readonly=True
    )
    commercial_config_text = fields.Text(
        compute="_compute_commercial_config_text",
        inverse="_inverse_commercial_config_text",
        string="Commercial Configuration",
    )

    def _compute_commercial_config_text(self):
        for record in self:
            record.commercial_config_text = json.dumps(record.commercial_config)

    def _inverse_commercial_config_text(self):
        for record in self:
            if record.commercial_config_text:
                record.commercial_config = json.loads(record.commercial_config_text)
