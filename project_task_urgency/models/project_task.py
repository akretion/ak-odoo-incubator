# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    is_urgent = fields.Boolean(
        string="Urgent",
        help="Check this box if the task is urgent.",
    )

    urgency_start_date = fields.Datetime(
        compute="_compute_urgency_start_date",
        store=True,
        help="The date when the task was marked as urgent.",
    )

    urgency_end_date = fields.Datetime(
        compute="_compute_urgency_end_date",
        store=True,
        help="The date when the urgent task was closed.",
    )

    urgency_duration = fields.Float(
        compute="_compute_urgency_duration",
        store=True,
        help="The duration of the task urgency in hours.",
    )

    @api.depends("is_urgent")
    def _compute_urgency_start_date(self):
        for task in self:
            if not task.is_closed and task.is_urgent:
                if not task.urgency_start_date:
                    task.urgency_start_date = fields.Datetime.now()
                task._notify_urgency()

    @api.depends("is_urgent", "state")
    def _compute_urgency_end_date(self):
        for task in self:
            if task.is_closed and task.is_urgent:
                if not task.urgency_end_date:
                    task.urgency_end_date = fields.Datetime.now()
                task._close_urgency()

    @api.depends("urgency_start_date", "urgency_end_date")
    def _compute_urgency_duration(self):
        for task in self:
            if task.urgency_start_date and task.urgency_end_date:
                task.urgency_duration = (
                    task.urgency_end_date - task.urgency_start_date
                ).total_seconds() / 3600.0
            else:
                task.urgency_duration = 0

    def _sync_user_activities(self):
        if not self.user_ids:
            for user in self.project_id.urgency_user_ids:
                if not self.activity_search(
                    ["project_task_urgency.mail_activity_data_urgency_to_assign"],
                    user_id=user.id,
                ):
                    self.activity_schedule(
                        "project_task_urgency.mail_activity_data_urgency_to_assign",
                        summary=_("Task marked as urgent to assign"),
                        note=_(
                            "The task has been marked as urgent and must be assigned."
                        ),
                        user_id=user.id,
                        date_deadline=fields.Date.context_today(self),
                    )
            return

        self.activity_feedback(
            ["project_task_urgency.mail_activity_data_urgency_to_assign"],
            feedback=_("Task was assigned to %s")
            % ", ".join(self.user_ids.mapped("name")),
        )
        users = self.user_ids
        user_activities = self.activity_search(
            ["project_task_urgency.mail_activity_data_urgency_todo"],
        ).mapped("user_id")

        for user in users - user_activities:
            self.activity_schedule(
                "project_task_urgency.mail_activity_data_urgency_todo",
                summary=_("Task marked as urgent"),
                note=_("The task has been marked as urgent and must be treated."),
                user_id=user.id,
                date_deadline=fields.Date.context_today(self),
            )
        for user in user_activities - users:
            self.activity_unlink(
                ["project_task_urgency.mail_activity_data_urgency_todo"],
                user_id=user.id,
            )

    def _notify_urgency(self):
        self.ensure_one()
        self._sync_user_activities()
        self.message_post(
            body=_("The task has been marked as urgent."),
            subtype_id=self.env.ref("mail.mt_note").id,
        )

    def _close_urgency(self):
        self.activity_feedback(
            ["project_task_urgency.mail_activity_data_urgency_to_assign"],
            feedback=_("Task was closed"),
        )
        self.activity_feedback(
            ["project_task_urgency.mail_activity_data_urgency_todo"],
            feedback=_("Task was closed"),
        )

    @api.model
    def _task_message_auto_subscribe_notify(self, users_per_task):
        res = super()._task_message_auto_subscribe_notify(users_per_task)
        for task, _users in users_per_task.items():
            if (
                not task.is_closed
                and task.is_urgent
                and not isinstance(task.id, models.NewId)
            ):
                task._sync_user_activities()
        return res
