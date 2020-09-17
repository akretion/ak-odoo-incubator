# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class AccountMoveExport(models.Model):
    _name = "account.move.export"
    _description = "Account Moves Export"
    _order = "id DESC"

    name = fields.Char(required=True)
    file_id = fields.Many2one(
        comodel_name="attachment.queue",
        string="File",
        compute="_compute_attachment",
        ondelete="cascade",
    )
    company_id = fields.Many2one(comodel_name="res.company", string="Company")

    def _compute_attachment(self):
        attachm = self.env["attachment.queue"].search(
            [("res_id", "in", self.ids), ("res_model", "=", self._name)]
        )
        mapping = {x.res_id: x.id for x in attachm}
        for rec in self:
            rec.file_id = mapping.get(rec.id)

    def action_goto_related_account_move(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "tree,form",
            "domain": [("export_id", "=", self.id)],
            "target": "current",
        }

    def _link_account_moves(self, move_ids):
        self.ensure_one()
        moves = self.env["account.move"].browse(move_ids)
        moves.write({"export_id": self.id})

    def _prepare_attachment(self, data, model, name=None):
        self.ensure_one()
        return {
            "datas": data.read(),
            "name": name or self.name,
            "res_id": self.id,
            "res_model": model,
            "datas_fname": "%s.csv" % self.name,
            "mimetype": "text/csv",
            "type": "binary",
            "task_id": self.env.ref(
                "account_move_export_traceability"
                ".account_move_export_task_synchronize"
            ).id,
        }

    def _create_attachment(self, data, model, name=None):
        self.ensure_one()
        self.env["attachment.queue"].create(
            self._prepare_attachment(data, model, name=name)
        )

    def action_download(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s/%s"
            % (self.file_id.attachment_id.id, self.file_id.datas_fname),
            "target": "self",
            "nodestroy": False,
        }


class AccountMove(models.Model):
    _inherit = "account.move"

    export_id = fields.Many2one(
        comodel_name="account.move.export", string="Export", readonly=True
    )
