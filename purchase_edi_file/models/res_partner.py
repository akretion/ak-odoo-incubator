#  Copyright (C) 2021 Akretion (http://www.akretion.com).

from odoo import _, exceptions, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _compute_edi_purchase_profile_ids(self):
        for partner in self:
            self.env["product.supplierinfo"].flush_model(
                ["partner_id", "purchase_edi_id"]
            )
            self.env.cr.execute(
                """
                SELECT DISTINCT purchase_edi_id
                FROM product_supplierinfo
                WHERE partner_id = %s
            """,
                (partner.id,),
            )
            ids_sql = self.env.cr.fetchall()
            profile_ids = [profile[0] for profile in ids_sql if profile[0]]
            if (
                partner.default_purchase_profile_id
                and partner.default_purchase_profile_id.id not in profile_ids
            ):
                profile_ids.append(partner.default_purchase_profile_id.id)
            partner.edi_purchase_profile_ids = profile_ids

    edi_purchase_profile_ids = fields.One2many(
        "ir.exports.config",
        compute="_compute_edi_purchase_profile_ids",
        string="Edi Purchase Profiles",
    )
    default_purchase_profile_id = fields.Many2one(
        "ir.exports.config",
        string="Default Purchase Profile",
        domain=[
            "|",
            ("resource", "=", "purchase.order.line"),
            ("resource", "=", False),
        ],
        help="If no profile is configured on product, this default "
        "profile will be used.",
    )
    edi_transport_config_id = fields.Many2one(
        "edi.transport.config", string="EDI Transport Configuration"
    )
    edi_empty_file = fields.Boolean(
        "Send EDI empty file",
        help="It may be usefull if the supplier always want to receive one file per "
        "profile",
    )

    def send_attachments_edi_by_mail(self, attachments, config, purchase=False):
        self.ensure_one()
        template = config.edi_mail_template_id
        if template.model_id.model == "res.partner":
            record = self.id
        elif template.model_id.model == "purchase.order":
            record = purchase
        else:
            raise exceptions.UserError(
                _("The mail template should be linked to partner or " "purchase order.")
            )
        mail_vals = {"attachment_ids": [(4, attach.id) for attach in attachments]}
        template.send_mail(record.id, email_values=mail_vals)

    def send_attachment_remote_server(self, attachments, config):
        storage_backend = config.edi_storage_backend_id
        exporting_tasks = storage_backend.synchronize_task_ids.filtered(
            lambda t: t.method_type == "export"
        )
        # do not manage multiple location for one partner for now.
        exporting_task = exporting_tasks and exporting_tasks[0]
        for attachment in attachments:
            self.env["attachment.queue"].create(
                {
                    "file_type": "export",
                    "task_id": exporting_task.id,
                    "attachment_id": attachment.id,
                }
            )

    def send_supplier_edi_attachments(self, attachments, config=False, purchase=False):
        self.ensure_one()
        if not config:
            config = self.edi_transport_config_id
        if not attachments or not config:
            return
        if config.edi_transfer_method == "mail":
            self.send_attachments_edi_by_mail(attachments, config, purchase=purchase)
        elif config.edi_transfer_method == "external_location":
            self.send_attachment_remote_server(attachments, config)
