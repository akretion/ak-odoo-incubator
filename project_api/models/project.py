# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools


class ProjectProject(models.Model):
    _inherit = "project.project"

    customer_project_name = fields.Char(
        help="Name that will appear on customer support menu", index=True
    )
    tag_ids = fields.Many2many("project.tags", string="Tags")
    subscribe_assigned_only = fields.Boolean(
        string="Subscribe assigned only",
        help="When a user get assigned, unscubscribe automaticaly other users",
    )


class ProjectTask(models.Model):
    _inherit = "project.task"

    stage_name = fields.Char(
        "Stage",
        compute="_compute_stage_name",
        inverse="_inverse_stage_name",
        store=True,
    )
    author_id = fields.Many2one(
        "res.partner",
        default=lambda self: self.env.user.partner_id.id,
        string="Create By",
    )
    partner_id = fields.Many2one(
        related="project_id.partner_id", readonly=True
    )
    user_id = fields.Many2one(default=False)
    assignee_id = fields.Many2one(
        "res.partner", compute="_compute_assignee", store=True
    )
    assignee_customer_id = fields.Many2one(
        "res.partner", string="Assignee To Customer", track_visibility="always"
    )
    origin_name = fields.Char()
    origin_url = fields.Char()
    origin_db = fields.Char()
    origin_model = fields.Char()
    technical_description = fields.Html()
    attachment_ids = fields.One2many(
        comodel_name="ir.attachment",
        inverse_name="res_id",
        domain=[("res_model", "=", "project.task")],
    )
    functional_area = fields.Selection(
        selection=[
            ("purchase", "Purchase"),
            ("account", "Account"),
            ("sale", "Sale"),
            ("stock", "Stock"),
            ("crm", "Crm"),
            ("procurement", "Procurement"),
            ("management", "Management"),
        ],
        string="Functional Area",
    )
    customer_report = fields.Html(
        compute="_compute_customer_report", store=True
    )

    customer_kanban_report = fields.Html(
        compute="_compute_customer_kanban_report", store=True
    )

    def _build_customer_kanban_report(self):
        # TODO we should find a better way
        # Implement your own template in your custom module
        return ""

    def _compute_customer_kanban_report(self):
        for record in self:
            record.customer_kanban_report =\
                record._build_customer_kanban_report()

    def _build_customer_report(self):
        # TODO we should find a better way
        # Implement your own template in your custom module
        return ""

    def _compute_customer_report(self):
        for record in self:
            record.customer_report = record._build_customer_report()

    @api.depends("user_id", "assignee_customer_id")
    def _compute_assignee(self):
        for record in self:
            record.assignee_id = (
                record.assignee_customer_id or record.user_id.partner_id
            )

    @api.depends("stage_id")
    def _compute_stage_name(self):
        for task in self:
            task.stage_name = task.stage_id.name

    def _inverse_stage_name(self):
        for task in self:
            stages = self.env["project.task.type"].search(
                [
                    ("project_ids", "in", [task.project_id.id]),
                    ("name", "=", task.stage_name),
                ]
            )
            if stages:
                task.stage_id = stages[0].id

    @api.multi
    @api.returns("self", lambda value: value.id)
    def message_post(
        self,
        body="",
        subject=None,
        message_type="notification",
        subtype=None,
        parent_id=False,
        attachments=None,
        content_subtype="html",
        **kwargs
    ):
        if self._context.get("force_message_author_id"):
            kwargs["author_id"] = self._context["force_message_author_id"]
        return super(ProjectTask, self).message_post(
            body=body,
            subject=subject,
            message_type=message_type,
            subtype=subtype,
            parent_id=parent_id,
            attachments=attachments,
            content_subtype=content_subtype,
            **kwargs
        )

    @api.model
    def create(self, vals):
        vals.pop("partner_id", None)  # readonly
        return super(ProjectTask, self).create(vals)

    def write(self, vals):
        vals.pop("partner_id", None)  # readonly
        if "user_id" in vals and self.project_id.subscribe_assigned_only:
            followers = self.message_follower_ids.mapped("partner_id")
            unsubscribe_users = self.env["res.users"].search(
                [
                    ("partner_id", "in", followers.ids),
                    ("id", "!=", vals["user_id"]),
                ]
            )
            self.message_unsubscribe_users(user_ids=unsubscribe_users.ids)
        return super(ProjectTask, self).write(vals)

    def message_auto_subscribe(self, updated_fields, values=None):
        super(ProjectTask, self).message_auto_subscribe(
            updated_fields, values=values
        )
        if values.get("author_id"):
            self.message_subscribe([values["author_id"]], force=False)
        if values.get("assignee_customer_id"):
            self.message_subscribe(
                [values["assignee_customer_id"]], force=False
            )
        return True

    def message_get_suggested_recipients(self):
        # we do not need this feature
        return {}

    @api.model
    def message_new(self, msg, custom_values=None):
        partner_email = tools.email_split(msg["from"])[0]
        # Automatically create a partner
        if not msg.get("author_id"):
            alias = tools.email_split(msg["to"])[0].split("@")[0]
            project = self.env["project.project"].search(
                [("alias_name", "=", alias)]
            )
            partner = self.env["res.partner"].create(
                {
                    "parent_id": project.partner_id.id,
                    "name": partner_email.split("@")[0],
                    "email": partner_email,
                }
            )
            msg["author_id"] = partner.id
        if custom_values is None:
            custom_values = {}
        custom_values.update(
            {"description": msg["body"], "author_id": msg["author_id"]}
        )
        return super(ProjectTask, self).message_new(
            msg, custom_values=custom_values
        )

    def _read_group_stage_ids(self, stages, domain, order):
        project_ids = self._context.get("stage_from_project_ids")
        if project_ids:
            projects = self.env["project.project"].browse(project_ids)
            stages |= projects.mapped("type_ids")
        return super(ProjectTask, self)._read_group_stage_ids(
            stages, domain, order
        )
