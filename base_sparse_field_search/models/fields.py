import json

from odoo import fields

from odoo.addons.base_sparse_field.models.fields import Serialized, monkey_patch

fields.Field.sparse_search = None


@monkey_patch(fields.Field)
def _get_attrs(self, model, name):
    attrs = _get_attrs.super(self, model, name)
    if attrs.get("sparse") and attrs.get("sparse_search"):
        attrs["search"] = self._search_sparse
    return attrs


@monkey_patch(fields.Field)
def _search_sparse(self, records, operator, value):
    return [(self.name, operator, value)]


# jsonb is returned as a json already by psycopg
@monkey_patch(Serialized)
def convert_to_record(self, value, record):
    return value if isinstance(value, dict) else json.loads(value or "{}")


Serialized.column_type = ("jsonb", "jsonb")
