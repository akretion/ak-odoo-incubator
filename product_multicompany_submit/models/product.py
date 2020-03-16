# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductTemplate(models.Model):
    _name = "product.template"
    _inherit = ["product.template", "base.multicompany.mixin"]

    def action_make_multicompany(self):
        self.company_id = False
