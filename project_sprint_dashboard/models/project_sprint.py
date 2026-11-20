# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import format_date

from odoo.addons.project_estimate_step.models.project_task import HOURS_PER_DAYS

DASHBOARD_LEVEL = 4
BUCKETS = ("done", "in_progress", "todo")


class ProjectSprint(models.Model):
    _inherit = "project.sprint"

    is_current = fields.Boolean(
        compute="_compute_is_current", search="_search_is_current"
    )

    def _compute_is_current(self):
        today = fields.Date.context_today(self)
        for sprint in self:
            sprint.is_current = bool(
                sprint.date_start
                and sprint.date_end
                and sprint.date_start <= today <= sprint.date_end
            )

    def _search_is_current(self, operator, value):
        today = fields.Date.context_today(self)
        domain = ["&", ("date_start", "<=", today), ("date_end", ">=", today)]
        if (operator == "=") != bool(value):
            return ["!", *domain]
        return domain

    @api.model
    def _get_dashboard_partners(self):
        projects = self.env["project.project"].search(
            [("use_sprint", "=", True), ("partner_id", "!=", False)]
        )
        return projects.partner_id.commercial_partner_id.sorted("name")

    @api.model
    def _get_dashboard_projects(self, partner):
        return self.env["project.project"].search(
            [("use_sprint", "=", True), ("partner_id", "child_of", partner.id)]
        )

    def _get_dashboard_bucket(self, task):
        self.ensure_one()
        if task.sprint_status == "canceled" or task.sprint_level_4_id != self:
            return False
        return task.sprint_status

    def _is_dashboard_carried_over(self, task):
        self.ensure_one()
        return any(
            sprint.date_start < self.date_start for sprint in task.sprint_history_ids
        )

    @api.model
    def _get_dashboard_days(self, task):
        if task.is_run and "effective_hours" in task._fields and task.effective_hours:
            return task.effective_hours / HOURS_PER_DAYS
        return task.estimate_step_id.days

    def _get_dashboard_buckets(self, tasks):
        self.ensure_one()
        res = {
            bucket: {"count": 0, "days": 0.0, "task_ids": []}
            for bucket in (*BUCKETS, "carried_over")
        }
        res["run"] = {"count": 0, "days": 0.0, "done_days": 0.0, "task_ids": []}
        for task in tasks:
            bucket = self._get_dashboard_bucket(task)
            if not bucket:
                continue
            days = self._get_dashboard_days(task)
            res[bucket]["count"] += 1
            res[bucket]["days"] += days
            res[bucket]["task_ids"].append(task.id)
            if self._is_dashboard_carried_over(task):
                res["carried_over"]["count"] += 1
                res["carried_over"]["days"] += days
                res["carried_over"]["task_ids"].append(task.id)
            if task.is_run:
                res["run"]["count"] += 1
                res["run"]["days"] += days
                res["run"]["task_ids"].append(task.id)
                if bucket == "done":
                    res["run"]["done_days"] += days
        return res

    @api.model
    def _get_dashboard_tasks(self, projects, sprints):
        return self.env["project.task"].search(
            [
                ("project_id", "in", projects.ids),
                ("sprint_level_4_id", "in", sprints.ids),
            ]
        )

    @api.model
    def get_sprint_dashboard_data(self, partner_id=False, sprint_id=False):
        partners = self._get_dashboard_partners()
        partner = (
            self.env["res.partner"].browse(partner_id) if partner_id else partners[:1]
        )
        level_domain = [("level", "=", DASHBOARD_LEVEL)]
        sprint = (
            self.browse(sprint_id)
            if sprint_id
            else self.search(
                [
                    *level_domain,
                    ("date_start", "<=", fields.Date.context_today(self)),
                ],
                order="date_start desc",
                limit=1,
            )
        )
        res = {
            "partners": [{"id": p.id, "name": p.display_name} for p in partners],
            "partner_id": partner.id,
            "sprint": False,
        }
        if not partner or not sprint:
            return res

        today = fields.Date.context_today(self)
        duration = (sprint.date_end - sprint.date_start).days + 1
        elapsed = min(max((today - sprint.date_start).days + 1, 0), duration)
        previous_sprints = self.search(
            [*level_domain, ("date_start", "<", sprint.date_start)],
            order="date_start desc",
            limit=5,
        )
        next_sprint = self.search(
            [*level_domain, ("date_start", ">", sprint.date_start)],
            order="date_start",
            limit=1,
        )
        history_sprints = (sprint | previous_sprints).sorted("date_start")
        projects = self._get_dashboard_projects(partner)
        tasks = self._get_dashboard_tasks(projects, history_sprints)

        res.update(
            {
                "sprint": {
                    "id": sprint.id,
                    "name": sprint.full_name,
                    "date_start": format_date(self.env, sprint.date_start),
                    "date_end": format_date(self.env, sprint.date_end),
                    "is_current": sprint.is_current,
                    "elapsed": elapsed,
                    "duration": duration,
                },
                "previous_id": previous_sprints[:1].id,
                "next_id": next_sprint.id,
                "totals": sprint._get_dashboard_buckets(tasks),
                "projects": [],
                "history": [],
            }
        )
        for project in projects:
            buckets = sprint._get_dashboard_buckets(
                tasks.filtered(lambda t, p=project: t.project_id == p)
            )
            count = sum(buckets[b]["count"] for b in BUCKETS)
            if count:
                res["projects"].append(
                    {
                        "id": project.id,
                        "name": project.display_name,
                        "buckets": buckets,
                        "count": count,
                    }
                )
        for hist_sprint in history_sprints:
            buckets = hist_sprint._get_dashboard_buckets(tasks)
            res["history"].append(
                {
                    "id": hist_sprint.id,
                    "name": " ".join(hist_sprint.full_name.split("/")[-2:]),
                    "done_days": buckets["done"]["days"],
                    "run_days": buckets["run"]["done_days"],
                    "planned_days": sum(buckets[b]["days"] for b in BUCKETS),
                }
            )
        return res
