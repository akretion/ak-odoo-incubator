# -*- coding: utf-8 -*-
from openerp import models, api


class AvailabeInPosMixin(models.AbstractModel):
    """Use link to categ_id instead of available_in_pos."""
    _name = 'categ.available_in_pos.abstract'
    _description = 'Available in POS via category'

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None,
                    order=None):
        # domain may be tuple or list, convert it to list in
        # order to modify it
        new_domain = map(list, domain)
        for lvl2 in domain:
            if lvl2[0] == 'available_in_pos':
                lvl2[0] = 'categ_id.available_in_pos'

        res = super(AvailabeInPosMixin, self).search_read(
            domain=new_domain, fields=fields, offset=offset,
            limit=limit, order=order)
        return res

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        # new_args may be tuple or list, convert it to list in
        # order to modify it
        new_args = map(list, args)
        for lvl2 in new_args:
            if lvl2[0] == 'available_in_pos':
                lvl2[0] = 'categ_id.available_in_pos'

        res = super(AvailabeInPosMixin, self).search(
            new_args, offset=offset, limit=limit,
            order=order, count=count)
        return res
