# -*- coding: utf-8 -*-
from odoo import models, api


class AvailabeInPosMixin(models.AbstractModel):
    """Use link to categ_id instead of available_in_pos."""
    _name = 'categ.available_in_pos.abstract'
    _description = 'Available in POS via category'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None,
                    order=None):
        for lvl2 in domain:
            if lvl2[0] == 'available_in_pos':
                lvl2[0] = 'categ_id.available_in_pos'

        res = super(AvailabeInPosMixin, self).search_read(
            domain=domain, fields=fields, offset=offset,
            limit=limit, order=order)
        return res

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        for lvl2 in args:
            if lvl2[0] == 'available_in_pos':
                lvl2[0] = 'categ_id.available_in_pos'

        res = super(AvailabeInPosMixin, self).search(
            args, offset=offset, limit=limit,
            order=order, count=count)
        return res
