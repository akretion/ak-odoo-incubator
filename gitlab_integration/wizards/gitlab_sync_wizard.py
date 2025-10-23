# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class GitlabSyncWizard(models.TransientModel):
    _name = "gitlab.sync.wizard"
    _description = "Gitlab Sync Wizard"

    gitlab_url = fields.Char(required=True)
    private_token = fields.Char(required=True)
    set_up_webhooks = fields.Boolean(default=True)
    webhook_url = fields.Char()
    webhook_secret_token = fields.Char()

    @property
    def gitlab_api_url(self):
        return f"{self.gitlab_url.rstrip('/')}/api/v4"

    def _get_gitlab_projects(self):
        api_url = f"{self.gitlab_api_url}/projects"
        headers = {"Private-Token": self.private_token}
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            raise UserError(
                _("Failed to connect to Gitlab: [%(status_code)s] %(response_text)s")
                % {"status_code": response.status_code, "response_text": response.text}
            )

    def _get_merge_requests_for_project(self, project):
        project_id = project["id"]
        api_url = f"{self.gitlab_api_url}/projects/{project_id}/merge_requests"
        headers = {"Private-Token": self.private_token}
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            _logger.warning(
                f"Failed to fetch MRs for project {project['name']}: "
                f"[{response.status_code}] {response.text}"
            )
            return []

    def _register_webhooks(self, projects):
        headers = {"Private-Token": self.private_token}
        registered_count = 0
        if not self.webhook_url:
            raise UserError(_("Webhook URL is required to set up webhooks."))
        if not self.webhook_secret_token:
            raise UserError(_("Webhook secret token is required to set up webhooks."))
        webhook_url = self.webhook_url.rstrip("/")
        for project in projects:
            project_id = project["id"]
            current_hooks_url = f"{self.gitlab_api_url}/projects/{project_id}/hooks"
            response = requests.get(current_hooks_url, headers=headers, timeout=10)
            if response.status_code == 200:
                existing_hooks = response.json()
                if any(hook["url"] == webhook_url for hook in existing_hooks):
                    _logger.info(
                        f"Webhook already exists for project {project['name']}."
                    )
                    continue
            else:
                _logger.warning(
                    f"Failed to fetch existing webhooks for project {project['name']}: "
                    f"[{response.status_code}] {response.text}"
                )
                continue

            api_url = f"{self.gitlab_api_url}/projects/{project_id}/hooks"
            data = {
                "url": webhook_url,
                "merge_requests_events": True,
                "token": self.webhook_secret_token,
            }
            response = requests.post(api_url, headers=headers, data=data, timeout=10)
            if response.status_code == 201:
                _logger.info(f"Webhook registered for project {project['name']}.")
                registered_count += 1
            else:
                _logger.warning(
                    f"Failed to register webhook for project {project['name']}: "
                    f"[{response.status_code}] {response.text}"
                )
        return registered_count

    def action_sync_gitlab(self):
        projects = self._get_gitlab_projects()
        total_mrs = 0
        total_webhooks = 0
        if projects:
            _logger.info(f"Found {len(projects)} projects in Gitlab.")
            for project in projects:
                mrs = self._get_merge_requests_for_project(project)
                _logger.info(
                    f"Project {project['name']} has {len(mrs)} merge requests."
                )
                total_mrs += len(mrs)
                if mrs:
                    self.env["gitlab.merge.request"].with_delay(
                        description=f"Gitlab MRs sync for project {project['name']}"
                    ).sync_merge_requests_for_project(project, mrs)

            if self.set_up_webhooks:
                total_webhooks += self._register_webhooks(projects)

        else:
            _logger.warning("No projects found in Gitlab.")

        _logger.info(f"Fetched {len(mrs)} merge requests from Gitlab.")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Gitlab Sync Queued"),
                "message": _(
                    "Queued sync of %(total_mrs)d merge requests for "
                    "projects: %(project_names)s.\n"
                    "%(total_webhooks)d webhooks registered."
                    % {
                        "total_mrs": total_mrs,
                        "project_names": ", ".join(
                            project["name"] for project in projects
                        ),
                        "total_webhooks": total_webhooks,
                    }
                ),
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
