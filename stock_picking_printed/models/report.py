# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class Report(models.Model):
    _inherit = 'report'

    # V8 api do not work here
    def get_pdf(self, cr, uid, docids, reportname, data=None, context=None):
        res = super(Report, self).get_pdf(
            cr, uid, docids, reportname, data=data, context=context)
        if reportname == 'stock.report_picking':
            self.pool['stock.picking'].set_printed(
                cr, uid, docids, context=context)
        return res
