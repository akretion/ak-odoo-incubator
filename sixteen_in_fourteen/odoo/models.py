# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.models import BaseModel, api


# read_kwargs backport from Odoo 16
def search_read(
    self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs
):
    """Perform a :meth:`search` followed by a :meth:`read`.

    :param domain: Search domain, see ``args`` parameter in :meth:`search`.
        Defaults to an empty domain that will match all records.
    :param fields: List of fields to read, see ``fields`` parameter in :meth:`read`.
        Defaults to all fields.
    :param int offset: Number of records to skip, see ``offset`` parameter in :meth:`search`.
        Defaults to 0.
    :param int limit: Maximum number of records to return, see ``limit`` parameter
    in :meth:`search`.
        Defaults to no limit.
    :param order: Columns to sort result, see ``order`` parameter in :meth:`search`.
        Defaults to no sort.
    :param read_kwargs: All read keywords arguments used to call
        ``read(..., **read_kwargs)`` method e.g. you can use
        ``search_read(..., load='')`` in order to avoid computing name_get
    :return: List of dictionaries containing the asked fields.
    :rtype: list(dict).
    """
    records = self.search(domain or [], offset=offset, limit=limit, order=order)
    if not records:
        return []

    if fields and fields == ["id"]:
        # shortcut read if we only want the ids
        return [{"id": record.id} for record in records]

    # read() ignores active_test, but it would forward it to any downstream search call
    # (e.g. for x2m or function fields), and this is not the desired behavior, the flag
    # was presumably only meant for the main search().
    # TODO: Move this to read() directly?
    if "active_test" in self._context:
        context = dict(self._context)
        del context["active_test"]
        records = records.with_context(context)

    result = records.read(fields, **read_kwargs)
    if len(result) <= 1:
        return result

    # reorder read
    index = {vals["id"]: vals for vals in result}
    return [index[record.id] for record in records if record.id in index]


BaseModel.search_read = api.model(search_read)
BaseModel._invalidate_cache = BaseModel.invalidate_cache

# This is suboptimal, this forces a flush all when it's not necessary
# but it's the safest way to backport this feature since a lot has changed in
# the cache flushing mechanism since Odoo 14.
BaseModel.flush_model = BaseModel.flush
BaseModel.flush_recordset = BaseModel.flush


def invalidate_model(self, fnames=None, flush=True):
    """Invalidate the cache of all records of ``self``'s model, when the
    cached values no longer correspond to the database values.  If the
    parameter is given, only the given fields are invalidated from cache.

    :param fnames: optional iterable of field names to invalidate
    :param flush: whether pending updates should be flushed before invalidation.
        It is ``True`` by default, which ensures cache consistency.
        Do not use this parameter unless you know what you are doing.
    """
    if flush:
        self.flush_model(fnames)
    self._invalidate_cache(fnames)


BaseModel.invalidate_model = invalidate_model


def invalidate_recordset(self, fnames=None, flush=True):
    """Invalidate the cache of the records in ``self``, when the cached
    values no longer correspond to the database values.  If the parameter
    is given, only the given fields on ``self`` are invalidated from cache.

    :param fnames: optional iterable of field names to invalidate
    :param flush: whether pending updates should be flushed before invalidation.
        It is ``True`` by default, which ensures cache consistency.
        Do not use this parameter unless you know what you are doing.
    """
    if flush:
        self.flush_recordset(fnames)
    self._invalidate_cache(fnames, self._ids)


BaseModel.invalidate_recordset = invalidate_recordset
