from openerp import fields
from openerp.addons.base_sparse_field.models.fields import monkey_patch


@monkey_patch(fields.Field)
def _setup_attrs(self, model, name):
    _setup_attrs.super(self, model, name)
    attrs = self._attrs
    if attrs.get("sparse") and attrs.get("sparse_search"):
        attrs["search"] = self._search_sparse
    for key in attrs:
        setattr(self, key, attrs[key])


@monkey_patch(fields.Field)
def _search_sparse(self, records, operator, value):
    return [(self.name, operator, value)]
