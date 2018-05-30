# -*- coding: utf-8 -*-
from odoo import models, api


class AvailabeInPosMixin(models.AbstractModel):
    """Use link to categ_id instead of available_in_pos."""
    _name = 'categ.available_in_pos.abstract'
    _description = 'Available in POS via category'

    @api.model
    def _available_in_pos_domain(self, domain):
        """Replace available_in_pos by categ_id.available_in_pos.

        ... in domains.
        @params domain: list or tuple
        @returns a new list
        """
        new_domain = []
        for lvl2 in domain:
            if lvl2[0] == 'available_in_pos':
                # because lvl2 may be a tuple
                # tuple is immutable
                new_lvl2 = list(lvl2)
                new_lvl2[0] = 'categ_id.available_in_pos'
                new_domain.append(new_lvl2)
            else:
                new_domain.append(lvl2)
        return new_domain

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None,
                    order=None):
        # prepend categ_id to available in pos
        new_domain = self._available_in_pos_domain(domain)
        return super(AvailabeInPosMixin, self).search_read(
            domain=new_domain, fields=fields, offset=offset,
            limit=limit, order=order)

    @api.model
    def search(self, args, offset=0, limit=0, order=None, count=False):
        # prepend categ_id to available in pos
        new_args = self._available_in_pos_domain(args)
        return super(AvailabeInPosMixin, self).search(
            new_args, offset=offset, limit=limit,
            order=order, count=count)
