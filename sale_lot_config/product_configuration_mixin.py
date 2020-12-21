# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien Beau <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields
import simplejson
import json


class ProductConfigurationMixin(models.AbstractModel):
    _name = 'product.configuration.mixin'
    _description = "Mixin to manage commercial and technical configuration"

    @api.multi
    def _get_configuration(self):
        for line in self:
            line.config_text = simplejson.dumps(line.config)

    @api.multi
    def _set_configuration(self):
        for line in self:
            if line.config_text:
                line.config = simplejson.loads(self.config_text)

    config = fields.Serialized(
        'Configuration',
        readonly=True,
        help="Allow to set custom configuration")
    config_text = fields.Text(
        compute='_get_configuration',
        inverse='_set_configuration',
        string='Configuration')
    commercial_config = fields.Serialized("Commercial Configuration", readonly=True)
    commercial_config_text = fields.Text(
        compute='_compute_commercial_config_text',
        inverse='_inverse_commercial_config_text',
        string='Commercial Configuration')

    @api.multi
    def _compute_commercial_config_text(self):
        for record in self:
            record.commercial_config_text = json.dumps(record.commercial_config)

    @api.multi
    def _inverse_commercial_config_text(self):
        for record in self:
            if record.commercial_config_text:
                record.commercial_config = json.loads(record.commercial_config_text)
