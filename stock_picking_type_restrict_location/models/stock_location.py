# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).


from openerp import api, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    @api.multi
    def belongs_to(self, location):
        self.ensure_one()
        if (
            self.parent_left >= location.parent_left
            and self.parent_right <= location.parent_right
        ):
            return True
        else:
            return False
