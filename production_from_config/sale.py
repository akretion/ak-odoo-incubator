# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
#        Sébastien Beau <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import simplejson
from openerp import api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.multi
    def _get_configuration(self):
        for line in self:
            line.config_text = simplejson.dumps(line.config)

    @api.multi
    def _set_configuration(self):
        for line in self:
            if self.config_text:
                line.config = simplejson.loads(self.config_text)

    config = fields.Serialized(
        "Configuration", readonly=True, help="Allow to set custom configuration"
    )
    config_text = fields.Text(
        compute="_get_configuration",
        inverse="_set_configuration",
        string="Configuration",
    )


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def _prepare_vals_lot_number(self, order_line, index_lot):
        res = super(SaleOrder, self)._prepare_vals_lot_number(order_line, index_lot)
        res["config"] = order_line.config
        return res
