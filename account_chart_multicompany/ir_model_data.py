# -*- coding: utf-8 -*-
###############################################################################
#
#   Module for OpenERP
#   Copyright (C) 2016 Akretion (http://www.akretion.com).
#   @author Chafique DELLI <chafique.delli@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    def _update(self, cr, uid, model, module, values, xml_id=False, store=True,
                noupdate=False, mode='init', res_id=False, context=None):
        if (module == 'account_chart_multicompany' and
            model in ('ir.rule') and
                xml_id == 'account.account_comp_rule'):
            mode = 'init'
        return super(IrModelData, self)._update(
            cr, uid, model, module, values, xml_id=xml_id, store=store,
            noupdate=noupdate, mode=mode, res_id=res_id, context=context)
