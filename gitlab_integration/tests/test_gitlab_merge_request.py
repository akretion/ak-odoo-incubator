# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessDenied

from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers.gitlab import gitlab_router
from .payloads import close, create, update


class TestGitlabMergeRequest(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = gitlab_router
        cls.default_fastapi_running_user = cls.env.ref(
            "gitlab_integration.gitlab_api_user"
        )
        cls.endpoint = cls.env["fastapi.endpoint"].create(
            {
                "name": "Gitlab Endpoint",
                "app": "gitlab",
                "root_path": "gitlab",
                "gitlab_token": "secure_token",
                "user_id": cls.default_fastapi_running_user.id,
            }
        )
        cls.default_fastapi_app = cls.endpoint._get_app()
        cls.default_fastapi_dependency_overrides = (
            cls.default_fastapi_app.dependency_overrides
        )
        cls.task_1 = cls.env.ref("project.project_1_task_1")
        cls.task_2 = cls.env.ref("project.project_1_task_2")
        cls.task_3 = cls.env.ref("project.project_2_task_3")

    def test_gitlab_webhook_invalid_token(self):
        with self._create_test_client() as test_client:
            with self.assertRaisesRegex(
                AccessDenied,
                "Invalid Gitlab token",
            ):
                test_client.post(
                    "/webhook",
                    headers={"X-Gitlab-Token": "invalid_token"},
                    json={},
                )

    def test_gitlab_webhook_good_token(self):
        with self._create_test_client() as test_client:
            response = test_client.post(
                "/webhook",
                headers={"X-Gitlab-Token": "secure_token"},
                json={"object_kind": "merge_request"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {"status": "ok"})

    def test_gitlab_webhook_no_token(self):
        with self._create_test_client(raise_server_exceptions=False) as test_client:
            response = test_client.post(
                "/webhook",
                json={},
            )
        self.assertEqual(response.status_code, 422)

    def test_gitlab_webhook_merge_request_created(self):
        self.assertFalse(self.task_1.gitlab_merge_request_ids)

        with self._create_test_client() as test_client:
            response = test_client.post(
                "/webhook",
                headers={"X-Gitlab-Token": "secure_token"},
                json=create(f"[{self.task_1.id}] Implement feature X"),
            )
        self.assertEqual(response.status_code, 200)
        merge_request = self.env["gitlab.merge.request"].search(
            [("gitlab_iid", "=", 3)], limit=1
        )
        self.assertTrue(merge_request)
        self.assertEqual(
            merge_request.name, "[%d] Implement feature X" % self.task_1.id
        )
        self.assertEqual(merge_request.state, "opened")
        self.assertEqual(merge_request.draft, False)
        self.assertEqual(merge_request.project_namespace, "Administrator")
        self.assertEqual(merge_request.project_name, "Test project")
        self.assertEqual(
            merge_request.web_url,
            "http://localhost:8929/root/test-project/-/merge_requests/3",
        )
        self.assertEqual(merge_request.task_ids, self.task_1)
        self.assertEqual(self.task_1.gitlab_merge_request_ids, merge_request)
        self.assertFalse(self.task_2.gitlab_merge_request_ids)
        self.assertFalse(self.task_3.gitlab_merge_request_ids)

    def test_gitlab_webhook_merge_request_double_created(self):
        self.assertFalse(self.task_1.gitlab_merge_request_ids)

        with self._create_test_client() as test_client:
            response = test_client.post(
                "/webhook",
                headers={"X-Gitlab-Token": "secure_token"},
                json=create(f"[{self.task_1.id}] Implement feature X"),
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.task_1.gitlab_merge_request_ids), 1)

        with self._create_test_client() as test_client:
            response = test_client.post(
                "/webhook",
                headers={"X-Gitlab-Token": "secure_token"},
                json=create(f"[{self.task_1.id}] Implement feature Y", iid=4),
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.task_1.gitlab_merge_request_ids), 2)

    def test_gitlab_webhook_merge_request_created_wrong_task_id(self):
        self.assertFalse(self.task_1.gitlab_merge_request_ids)

        with self._create_test_client() as test_client:
            response = test_client.post(
                "/webhook",
                headers={"X-Gitlab-Token": "secure_token"},
                json=create(f"[66879954][{self.task_1.id}] Implement feature X"),
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.task_1.gitlab_merge_request_ids), 1)

    def test_gitlab_webhook_merge_request_updated(self):
        self.assertFalse(self.task_1.gitlab_merge_request_ids)

        with self._create_test_client() as test_client:
            response = test_client.post(
                "/webhook",
                headers={"X-Gitlab-Token": "secure_token"},
                json=create(f"[{self.task_1.id}] Implement feature X"),
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.task_1.gitlab_merge_request_ids), 1)
        self.assertFalse(self.task_2.gitlab_merge_request_ids)
        self.assertFalse(self.task_3.gitlab_merge_request_ids)

        with self._create_test_client() as test_client:
            response = test_client.post(
                "/webhook",
                headers={"X-Gitlab-Token": "secure_token"},
                json=update(
                    f"[{self.task_2.id}] [{self.task_3.id}] Implement feature X"
                ),
            )
        self.assertEqual(response.status_code, 200)

        self.assertFalse(self.task_1.gitlab_merge_request_ids)
        self.assertEqual(len(self.task_2.gitlab_merge_request_ids), 1)
        self.assertEqual(len(self.task_3.gitlab_merge_request_ids), 1)

    def test_gitlab_webhook_merge_request_closed(self):
        self.assertFalse(self.task_1.gitlab_merge_request_ids)

        with self._create_test_client() as test_client:
            response = test_client.post(
                "/webhook",
                headers={"X-Gitlab-Token": "secure_token"},
                json=create(f"[{self.task_1.id}] Implement feature X"),
            )
        self.assertEqual(response.status_code, 200)

        merge_request = self.env["gitlab.merge.request"].search(
            [("gitlab_iid", "=", 3)], limit=1
        )
        self.assertEqual(merge_request.state, "opened")

        with self._create_test_client() as test_client:
            response = test_client.post(
                "/webhook",
                headers={"X-Gitlab-Token": "secure_token"},
                json=close(f"[{self.task_1.id}] Implement feature X"),
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(merge_request.state, "closed")
