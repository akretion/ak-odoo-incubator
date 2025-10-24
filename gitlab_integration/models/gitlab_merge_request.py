# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import re

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Tasks ids are handled as [id] [id2] in the beginning of the merge request title
TASK_REFS_REGEX = re.compile(r"^(?:\s*Draft:\s*)?(?:\s*\[[0-9, ]+\]\s*)+")
TASK_REF_REGEX = re.compile(r"\[([0-9, ]+)\]")


def extract_task_ids_from_title(title: str) -> list[int]:
    """Extract task IDs from the merge request title.

    Args:
        title (str): The title of the merge request.
    Returns:
        list[int]: A list of task IDs.
    """
    match = TASK_REFS_REGEX.match(title)
    if not match:
        return []

    tasks = TASK_REF_REGEX.findall(match.group(0))
    return (
        [int(task.replace(",", "").replace(" ", "")) for task in tasks] if tasks else []
    )


class GitlabMergeRequest(models.Model):
    _name = "gitlab.merge.request"
    _description = "Gitlab Merge Request"

    name = fields.Char(string="Title", required=True)
    description = fields.Text()
    draft = fields.Boolean(default=False)
    state = fields.Selection(
        [
            ("opened", "Opened"),
            ("closed", "Closed"),
            ("merged", "Merged"),
            ("locked", "Locked"),
        ],
        required=True,
        default="opened",
    )
    gitlab_iid = fields.Integer(required=True)
    # Make a model?
    project_path = fields.Char(required=True)
    project_namespace = fields.Char()
    project_name = fields.Char()

    web_url = fields.Char()

    task_ids = fields.Many2many(
        comodel_name="project.task",
        string="Related Tasks",
        help="Odoo Tasks associated with this Gitlab Merge Request.",
    )

    def _get_tasks_from_merge_request_title(self, title: str):
        """Extract task references from the merge request title.

        Args:
            title (str): The title of the merge request.
        Returns:
            recordset: A recordset of project.task records.
        """
        task_ids = extract_task_ids_from_title(title)
        return self.env["project.task"].browse(task_ids).exists()

    def _filter_allowed_tasks(self, tasks, gitlab_project_id: int):
        """Filter tasks based on allowed Gitlab project IDs in their projects.

        Args:
            tasks (recordset): A recordset of project.task records.
            gitlab_project_id (int): The Gitlab project ID to check against.
        Returns:
            recordset: A filtered recordset of project.task records.
        """
        allowed_tasks = tasks.sudo().filtered(
            lambda task: gitlab_project_id
            in [
                int(pid.strip())
                for pid in (task.project_id.allowed_gitlab_id_projects or "").split(",")
                if pid.strip().isdigit()
            ]
        )
        disallowed_tasks = tasks - allowed_tasks
        if disallowed_tasks:
            _logger.info(
                f"Tasks {disallowed_tasks.ids} are not linked to allowed "
                f"Gitlab project ID {gitlab_project_id} and will be ignored."
            )
        return allowed_tasks.sudo(False)

    @api.model
    def process_webhook(self, payload: dict) -> None:
        """Process a Gitlab Merge Request webhook payload.

        Args:
            payload (dict): The webhook payload from Gitlab.
        """
        project_data = payload.get("project", {})
        mr_data = payload.get("object_attributes", {})
        gitlab_iid = mr_data.get("iid")
        if not gitlab_iid:
            _logger.warning(f"No IID found in merge request data. Payload: {payload}")
            return

        merge_request = self.search([("gitlab_iid", "=", gitlab_iid)], limit=1)
        name = mr_data.get("title")

        tasks = self._filter_allowed_tasks(
            self._get_tasks_from_merge_request_title(name),
            project_data.get("id"),
        )
        if not tasks:
            _logger.info(
                f"No valid tasks found in merge request IID {gitlab_iid} title. "
                "Ignoring merge request."
            )
            return
        vals = {
            "name": name,
            "description": mr_data.get("description"),
            "draft": mr_data.get("work_in_progress", False),
            "state": mr_data.get("state"),
            "project_path": project_data.get("path_with_namespace"),
            "project_namespace": project_data["namespace"]
            if isinstance(project_data.get("namespace"), str)
            else project_data.get("namespace", {}).get("name"),
            "project_name": project_data.get("name"),
            "web_url": mr_data.get("web_url", mr_data.get("url")),
            "task_ids": [(6, 0, tasks.ids)],
        }
        if merge_request:
            merge_request.write(vals)
        else:
            vals["gitlab_iid"] = gitlab_iid
            self.create(vals)

    @api.model
    def sync_merge_requests_for_project(
        self, project: dict, merge_requests: list[dict]
    ) -> None:
        for mr in merge_requests:
            payload = {
                "project": project,
                "object_attributes": mr,
            }
            self.process_webhook(payload)
        return (
            f"{len(merge_requests)} merge requests synced "
            f"({', '.join(str(mr['iid']) for mr in merge_requests)})."
        )
