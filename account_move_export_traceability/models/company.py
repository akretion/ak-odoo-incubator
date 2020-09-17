# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date
import logging

from odoo import _, api, models, fields
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    account_move_export_period = fields.Selection(
        selection="_get_account_move_export_period",
        string="Journal Entries Export Period",
        help="Choose an export periodicity for journal entries of this company",
    )

    def _get_account_move_export_period(self):
        # TODO implements Weekly here if needed
        return [
            ("daily", "Daily"),
        ]

    def _get_my_export_method(self):
        """ To override in your custom module without call super """
        raise UserError(
            "You should specify a method to extract entries in your companies"
        )

    @api.model
    def extract_account_move_scheduler(self):
        """ Triggered by a cron """
        query = """
            SELECT company_id, max(create_date::date) as date
            FROM account_move_export
            GROUP BY company_id """
        self.env.cr.execute(query)
        dates = {x["company_id"]: x["date"] for x in self.env.cr.dictfetchall()}
        companies = self.search([("account_move_export_period", "=", "daily")])
        for rec in companies:
            if not dates.get(rec.id) or date.today() > dates.get(rec.id):
                journals = (
                    self.env["account.journal"]
                    .sudo()
                    .search(
                        [
                            ("company_id", "=", rec.id),
                            ("type", "!=", "general"),
                        ]
                    )
                )
                wizard = (
                    self.env["account.csv.export"]
                    .sudo()
                    .create(
                        {
                            "date_start": "2000-01-01",
                            "date_end": date.today(),
                            "company_id": rec.id,
                            "journal_ids": [(6, 0, journals.ids)],
                            "mark_exported_record": True,
                        }
                    )
                )
                method = getattr(wizard, self._get_my_export_method())
                export = method()
                if export:
                    logger.info("Produced file %s %s", export.name, export.id)
                else:
                    logger.info(
                        "No entries data matching with date for company %s ", rec.name
                    )
            else:
                logger.info("No journal entries data for company %s ", rec.name)


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    account_move_export_period = fields.Selection(
        readonly=False,
        related="company_id.account_move_export_period",
    )
