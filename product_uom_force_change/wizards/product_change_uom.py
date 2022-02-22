# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

SKIP_TABLE = [
    "res_config_settings",
    "res_company",
    "product_template",
    "product_change_uom",
    "stock_quant_package",
    "rma_split_wizard",
    "stock_location_storage_type",
]


class ProductChangeUom(models.TransientModel):
    _name = "product.change.uom"
    _description = "Product Change Uom"

    new_uom_id = fields.Many2one("uom.uom")

    def _get_all_table(self):
        self._cr.execute(
            """
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND ccu.table_name = 'uom_uom' and ccu.column_name = 'id'
            """
        )
        return [x for x in self._cr.fetchall() if x[0] not in SKIP_TABLE]

    def run(self):
        self = self.sudo().with_context(active_test=False)
        tmpls = self.env["product.template"].browse(self._context.get("active_ids"))
        table2model = {model._table: model for model in self.env.values()}
        for tmpl in tmpls:
            current_uom = tmpl.uom_id
            for table, uom_field in self._get_all_table():
                if table not in table2model:
                    _logger.debug("The table %s is deprecated, skip it", table)
                    continue
                model = table2model[table]
                if uom_field not in model._fields:
                    _logger.debug(
                        "The field %s on model %s is deprecated, skip it",
                        uom_field,
                        model._name,
                    )
                    continue
                if "product_id" in model._fields:
                    records = model.search(
                        [("product_id", "in", tmpl.product_variant_ids.ids)]
                    )
                    if records:
                        for record in records:
                            if record[uom_field] != current_uom:
                                raise UserError(
                                    _(
                                        "Impossible to change the uom, because the "
                                        "record {} {} {} use the uom {}"
                                    ).format(
                                        model._name,
                                        record.id,
                                        model._rec_name,
                                        record[uom_field],
                                    )
                                )
                        _logger.info(
                            "Update %s records with uom on %s, field %s",
                            len(records),
                            model._name,
                            uom_field,
                        )
                        self._cr.execute(
                            f"UPDATE {table} SET {uom_field}=%s WHERE id in %s",
                            (self.new_uom_id.id, tuple(records.ids)),
                        )
                else:
                    raise UserError(
                        _("Fail to found product_id for table {}").format(table)
                    )

            self._cr.execute(
                "UPDATE product_template SET uom_id=%s, uom_po_id=%s WHERE id = %s",
                (self.new_uom_id.id, self.new_uom_id.id, tmpl.id),
            )
            if "uom_intercompany_id" in tmpl._fields:
                if tmpl.uom_intercompany_id:
                    self._cr.execute(
                        "UPDATE product_template SET uom_intercompany_id=%s "
                        "WHERE id = %s",
                        (self.new_uom_id.id, tmpl.id),
                    )
        return True
