from odoo import _, fields, models


class PrintConfig(models.Model):
    _inherit = "print.config"

    server = fields.Char(
        string="🖥 Server",
        required=True,
        help="IP or name resolved by your internal DNS",
    )
    port = fields.Integer()
    warehouse_id = fields.Many2one(comodel_name="stock.warehouse")
    company_id = fields.Many2one(comodel_name="res.company")
    printer_ids = fields.One2many(comodel_name="printer", inverse_name="config_id")
    printer_name_missing = fields.Char(
        compute="_compute_missing_printer_name",
        store=False,
        help="Printers may be imported without names. User should adjust it",
    )

    def _compute_missing_printer_name(self):
        for rec in self:
            alert = ""
            if rec.printer_ids.filtered(lambda s: not s.name):
                alert = _("⛔ Missing name on at least one printer")
            rec.printer_name_missing = alert
