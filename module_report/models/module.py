# coding: utf-8
# © 2016 David BEAL @ Akretion <david.beal@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict, OrderedDict
import logging

from openerp import models, fields, api

from .author_mapping import AUTHORS_MAP

logger = logging.getLogger(__name__)

AUTHORS = AUTHORS_MAP.keys()


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    # _rpt_module_count = None

    @api.multi
    def _get_authors(self):
        authors = defaultdict(int)
        module_authors = OrderedDict()
        for rec in self:
            raw_authors = [unicode(x) for x in rec.author.split(',')]
            for author in raw_authors:
                auth = author.strip()
                for elm in ("[]'\""):
                    auth = auth.replace(elm, '')
                authors[unicode(self._filter_authors(auth))] += 1
            self._clean_falsy(authors)
        self._search_homonyns(authors)
        for author in sorted(authors, key=authors.get, reverse=True):
            module_authors[unicode(author).encode('utf-8')] = authors[author]
        return module_authors

    @api.multi
    def _module_count(self):
        return len(self)

    def _filter_authors(self, author):
        if author.lower() in AUTHORS:
            author = AUTHORS_MAP[author.lower()]
        return author

    def _search_homonyns(self, authors):
        probably_homonyms = {}
        falsy = [u'Odoo Community Association (OCA)', u'OdooMRP team']
        for author in authors:
            for auth_string in authors.keys():
                if author.lower() in auth_string.lower() and \
                        author != auth_string:
                    homonyn = True
                    for ambiguous in falsy:
                        if author in ambiguous:
                            homonyn = False
                    if homonyn:
                        probably_homonyms[auth_string] = author
        if probably_homonyms:
            logger.warning("Seems there are homonyns in module authors \n %s",
                           probably_homonyms)

    def _clean_falsy(self, authors):
        for falsy in [u'', u'S.L.']:
            if falsy in authors:
                del authors[falsy]
