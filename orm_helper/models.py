# -*- coding: utf-8 -*-
# © 2015 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


@api.multi
def merge_duplicate(self, record_ids):
    self._cr.execute("""SELECT
            cl1.relname as table,
            att1.attname as column
        FROM pg_constraint as con, pg_class as cl1, pg_class as cl2,
            pg_attribute as att1, pg_attribute as att2
        WHERE con.conrelid = cl1.oid
            AND con.confrelid = cl2.oid
            AND array_lower(con.conkey, 1) = 1
            AND con.conkey[1] = att1.attnum
            AND att1.attrelid = cl1.oid
            AND cl2.relname = %s
            AND att2.attname = 'id'
            AND array_lower(con.confkey, 1) = 1
            AND con.confkey[1] = att2.attnum
            AND att2.attrelid = cl2.oid
            AND con.contype = 'f'""", (self._table,))
    for table, field in self._cr.fetchall():
        self._cr.execute((
            "UPDATE " + table +
            " SET " + field + "= %s " +
            "WHERE " + field + " in %s"),
            (self.id, tuple(record_ids)))
    self.browse(record_ids).unlink()

models.Model.merge_duplicate = merge_duplicate
