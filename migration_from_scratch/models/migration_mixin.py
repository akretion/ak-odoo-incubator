# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


import collections

from psycopg2 import sql

from odoo import _, exceptions, fields, models

from ..sql_db import get_external_cursor

# mapping dict options : old_name (renaming of field), migration_method,
# if we need to transfort the data
# {"old_table": "account_account_tax_default_rel",
# "old_col1": "account_id", "old_col2": "tax_id"} # for m2m


class MigrationMixin(models.AbstractModel):
    _name = "migration.mixin"
    _description = "Mixing  to help migrate data from another odoo database"

    _update_allowed = True
    old_table_name = ""
    unique_field = "old_odoo_id"

    old_odoo_id = fields.Integer("Id in previous Odoo version", index=True, copy=False)

    def mapped_fields_default(self):
        return {}

    @property
    def mapped_fields(self):
        default = self.mapped_fields_default()
        default.update({"old_odoo_id": {"old_name": "id"}})
        return default

    def _old_data_query(self, domain):
        select_list = []
        all_fields = self._fields
        table_name = self.old_table_name or self._table
        query = self._where_calc(domain)
        if self.old_table_name:
            # replace in the query the from table but keep the old_alias to avoid issue
            # in where clauses. exemple with stock_lot, we'd have
            # from stock_production_lot as stock_lot
            table_name = self.old_table_name
            query._tables[self._table] = table_name
        for field_name, options in self.mapped_fields.items():
            # many2many have no fields on table, it is a separated table
            # so we ignore these fields in the select query, it will be managed
            # during the update.
            if all_fields[field_name].type == "many2many":
                continue

            old_field_name = options.get("old_name") or field_name
            if options.get("inherits"):
                inherited_model = self.env[options["inherits"]]
                field_table_name = (
                    hasattr(inherited_model, "old_table_name")
                    and inherited_model.old_table_name
                    or inherited_model._table
                )
                alias = query.join(
                    table_name,
                    self._inherits[options["inherits"]],
                    field_table_name,
                    "id",
                    self._inherits[options["inherits"]],
                )
            else:
                alias = table_name
            select_list.append("%s.%s as %s" % (alias, old_field_name, field_name))
        select_query = ",".join(select_list)
        from_clause, where_clause, where_clause_params = query.get_sql()
        where_clause = where_clause and "WHERE %s" % where_clause or ""
        query = """
            SELECT %(select_fields)s
            FROM %(from_clause)s
            %(where)s
        """ % {
            "select_fields": select_query,
            "from_clause": from_clause,
            "where": where_clause,
        }
        return query, where_clause_params

    def _get_old_data(self, domain, old_cr):
        query, params = self._old_data_query(domain)
        old_cr.execute(query, params)
        old_data = old_cr.dictfetchall()
        return old_data

    def _get_old_m2m_data(self, old_cr):
        all_fields = self._fields
        old_m2m_data = {}
        for new_field, options in self.mapped_fields.items():
            if all_fields[new_field].type == "many2many":
                query = sql.SQL("SELECT {col1}, {col2} FROM {table}").format(
                    col1=sql.Identifier(options["old_col1"]),
                    col2=sql.Identifier(options["old_col2"]),
                    table=sql.Identifier(options["old_table"]),
                )
                old_cr.execute(query)
                old_m2m_data[new_field] = old_cr.fetchall()
        return old_m2m_data

    def get_old_data(self, domain):
        old_cr = get_external_cursor()
        old_data = self._get_old_data(domain, old_cr)
        old_m2m_data = self._get_old_m2m_data(old_cr)
        old_cr.close()
        return old_data, old_m2m_data

    def migrate_data(self, batch=0, domain=None):
        if domain is None:
            domain = []
        data, m2m_data = self.get_old_data(domain)
        if batch:
            for i in range(0, len(data), batch):
                ongoing_data = data[i : i + batch]
                new_records = updated_records = self.browse(False)
                self.with_delay().import_old_data(ongoing_data, m2m_data)
        else:
            new_records, updated_records = self.import_old_data(data, m2m_data)
        return new_records, updated_records

    def _get_m2m_id_mapping(self, m2m_data):
        all_fields = self._fields
        m2m_id_mapping = {}
        for m2m_field_name, m2m_field_data in m2m_data.items():
            m2m_field = all_fields[m2m_field_name]
            comodel_id_mapping = self.env[m2m_field.comodel_name]._get_id_mapping()
            m2m_id_mapping[m2m_field_name] = collections.defaultdict(list)
            for old_id, old_comodel_id in m2m_field_data:
                comodel_new_id = comodel_id_mapping.get(old_comodel_id, False)
                if comodel_new_id:
                    m2m_id_mapping[m2m_field_name][old_id].append(comodel_new_id)
            return m2m_id_mapping

    def _transform_data(self, data, m2m_data):
        m2m_id_mapping = self._get_m2m_id_mapping(m2m_data)
        all_fields = self._fields
        # Create all m2x mapping dict (to avoid search on each row of the loop
        m2o_id_mapping = {}
        for field_name, _options in self.mapped_fields.items():
            myfield = all_fields[field_name]
            if myfield.type == "many2one":
                m2o_id_mapping[field_name] = self.env[
                    myfield.comodel_name
                ]._get_id_mapping()
        # loop on data to transform it with new version data
        for record_data in data:
            for field_name, options in self.mapped_fields.items():
                if options.get("migration_method"):
                    new_val = getattr(self, options["migration_method"])(
                        record_data[field_name]
                    )
                    record_data[field_name] = new_val
                myfield = all_fields[field_name]
                if myfield.type == "many2one":
                    new_val = m2o_id_mapping[field_name].get(
                        record_data[field_name], False
                    )  # TODO manage error ? in case we got old id and not new ?
                    record_data[field_name] = new_val
                if myfield.type == "many2many":
                    old_id = record_data["old_odoo_id"]
                    new_ids = m2m_id_mapping[field_name].get(old_id, [])
                    record_data[field_name] = [(6, 0, new_ids)]
        return data

    def import_old_data(self, data, m2m_data):
        transformed_data = self._transform_data(data, m2m_data)
        new_records, updated_records = self.create_or_update_from_old_data(
            transformed_data
        )
        self._after_import(new_records, updated_records, transformed_data)
        return new_records, updated_records

    def _get_id_mapping(self):
        read_data = self.search_read([("old_odoo_id", ">", 0)], ["id", "old_odoo_id"])
        return {x["old_odoo_id"]: x["id"] for x in read_data}

    # still usefull ? maybe not since we search in batch with
    # _get_existing_records_by_unique_field
    def _get_existing_record(self, vals):
        ref_field = self.unique_field
        ref_val = vals.get(ref_field)
        domain = [(ref_field, "=", ref_val)]
        record = self.search(domain)
        if len(record) > 1:
            raise exceptions.UserError(
                _(
                    "Too much records found (%(record_size)s) for %(field)s with value %(val)s"
                )
                % {"record_size": len(record), "field": ref_field, "val": ref_val}
            )
        return record

    def _get_existing_records_by_unique_field(self):
        ref_field = self.unique_field
        read_data = self.with_context(active_test=False).search_read(
            [(ref_field, "!=", False)], [ref_field]
        )
        return {x[ref_field]: x["id"] for x in read_data}

    def create_or_update_from_old_data(self, data):
        create_vals_list = []
        created_records = self.browse(False)
        updated_records = self.browse(False)

        existing_record_mapping = self._get_existing_records_by_unique_field()
        ref_field = self.unique_field
        for rec_vals in data:
            record_id = existing_record_mapping.get(rec_vals[ref_field], False)
            if record_id:
                if not self._update_allowed:
                    continue
                # do not updated ref_field as it is not needed and we avoid
                # trigerring possible constraint on it..
                rec_vals.pop(ref_field)
                record = self.browse(record_id)
                record.write(rec_vals)
                updated_records |= record
            else:
                create_vals_list.append(rec_vals)
        if create_vals_list:
            created_records = self.create(create_vals_list)
        return created_records, updated_records

    def _after_import(self, new_records, updated_records, transformed_data):
        return
