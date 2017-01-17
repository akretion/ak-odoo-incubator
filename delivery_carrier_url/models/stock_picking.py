# -*- coding: utf-8 -*-
#  Copyright (C) 2017 Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, api
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def open_tracking_url(self):
        self.ensure_one()
        packages = self._get_packages_from_picking()
        if not packages:
            raise UserError(_('This shipping has no packages.'))
        if len(packages) > 1:
            action = self.env.ref('stock.action_package_view')
            client_action = action.read()[0]
            client_action['res_id'] = packages.ids
            client_action['domain'] = \
                "[('id','in',[" + ','.join(map(str, packages.ids)) + "])]"
            client_action['context'] = "{'picking_id': " + str(self.id) + "}"
        else:
            client_action = packages.with_context(
                picking=self
            ).open_tracking_url()
        return client_action
