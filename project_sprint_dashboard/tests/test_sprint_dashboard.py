# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.tests import TransactionCase, tagged


@freeze_time("2023-07-24")
@tagged("post_install", "-at_install")
class TestSprintDashboard(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        Sprint = cls.env["project.sprint"]
        year = Sprint.create(
            {"name": "2023", "date_start": "2023-01-02", "date_end": "2023-12-29"}
        )
        quarter = Sprint.create(
            {
                "name": "Q3",
                "parent_id": year.id,
                "date_start": "2023-07-03",
                "date_end": "2023-09-29",
            }
        )
        month = Sprint.create(
            {
                "name": "July",
                "parent_id": quarter.id,
                "date_start": "2023-07-03",
                "date_end": "2023-08-04",
            }
        )
        cls.sprint_1 = Sprint.create(
            {
                "name": "F1",
                "parent_id": month.id,
                "date_start": "2023-07-10",
                "date_end": "2023-07-21",
            }
        )
        cls.sprint_2 = Sprint.create(
            {
                "name": "F2",
                "parent_id": month.id,
                "date_start": "2023-07-24",
                "date_end": "2023-08-04",
            }
        )
        cls.step = cls.env["project.estimate.step"].create(
            {"name": "2 days", "days": 2}
        )
        cls.customer = cls.env["res.partner"].create(
            {"name": "Customer", "is_company": True}
        )
        cls.other_customer = cls.env["res.partner"].create({"name": "Other"})
        cls.project = cls.env["project.project"].create(
            {
                "name": "Customer project",
                "use_sprint": True,
                "partner_id": cls.customer.id,
                "estimate_step_ids": [(6, 0, cls.step.ids)],
            }
        )
        cls.other_project = cls.env["project.project"].create(
            {
                "name": "Other project",
                "use_sprint": True,
                "partner_id": cls.other_customer.id,
            }
        )
        cls.bug_tag = cls.env["project.tags"].create(
            {"name": "Sprint dashboard run test"}
        )

    def _create_task(self, sprint, project=None, **vals):
        return self.env["project.task"].create(
            {
                "name": "Task",
                "project_id": (project or self.project).id,
                "sprint_id": sprint.id,
                **vals,
            }
        )

    def _get_data(self, sprint=None, partner=None):
        return self.env["project.sprint"].get_sprint_dashboard_data(
            partner_id=(partner or self.customer).id,
            sprint_id=sprint.id if sprint else False,
        )

    def test_sprint_status(self):
        task = self._create_task(self.sprint_2)
        self.assertEqual(task.sprint_status, "todo")
        task.estimate_step_id = self.step
        self.assertEqual(task.sprint_status, "in_progress")
        task.state = "04_waiting_normal"
        self.assertEqual(task.sprint_status, "todo")
        task.state = "1_done"
        self.assertEqual(task.sprint_status, "done")
        task.state = "1_canceled"
        self.assertEqual(task.sprint_status, "canceled")

    def test_is_current(self):
        self.assertFalse(self.sprint_1.is_current)
        self.assertTrue(self.sprint_2.is_current)
        current = self.env["project.sprint"].search(
            [("level", "=", 4), ("is_current", "=", True)]
        )
        self.assertEqual(current, self.sprint_2)
        not_current = self.env["project.sprint"].search(
            [("level", "=", 4), ("is_current", "=", False)]
        )
        self.assertIn(self.sprint_1, not_current)
        self.assertNotIn(self.sprint_2, not_current)

    def test_history_and_carried_over(self):
        task = self._create_task(self.sprint_1, estimate_step_id=self.step.id)
        self.assertEqual(task.sprint_history_ids, self.sprint_1)
        task.sprint_id = self.sprint_2
        self.assertEqual(task.sprint_history_ids, self.sprint_1 | self.sprint_2)

        data = self._get_data(self.sprint_1)
        self.assertEqual(data["totals"]["carried_over"]["count"], 0)
        self.assertEqual(data["totals"]["in_progress"]["count"], 0)
        self.assertFalse(data["projects"])
        self.assertEqual(data["next_id"], self.sprint_2.id)

        data = self._get_data(self.sprint_2)
        self.assertEqual(data["totals"]["in_progress"]["count"], 1)
        self.assertEqual(data["totals"]["in_progress"]["days"], 2)
        self.assertEqual(data["totals"]["carried_over"]["count"], 1)
        self.assertEqual(data["totals"]["carried_over"]["task_ids"], task.ids)
        self.assertEqual(data["projects"][0]["count"], 1)
        self.assertEqual(data["previous_id"], self.sprint_1.id)

        task.state = "1_done"
        data = self._get_data(self.sprint_2)
        self.assertEqual(data["totals"]["done"]["count"], 1)
        self.assertEqual(data["totals"]["carried_over"]["count"], 1)

    def test_dashboard_default_sprint_and_projects(self):
        self._create_task(self.sprint_2, estimate_step_id=self.step.id, state="1_done")
        self._create_task(self.sprint_2, state="1_canceled")
        self._create_task(self.sprint_2, project=self.other_project)

        data = self._get_data()
        self.assertEqual(data["sprint"]["id"], self.sprint_2.id)
        self.assertTrue(data["sprint"]["is_current"])
        self.assertEqual(len(data["projects"]), 1)
        project_data = data["projects"][0]
        self.assertEqual(project_data["id"], self.project.id)
        self.assertEqual(project_data["count"], 1)
        self.assertEqual(project_data["buckets"]["done"]["days"], 2)
        history = {h["id"]: h for h in data["history"]}
        self.assertEqual(history[self.sprint_2.id]["done_days"], 2)
        self.assertEqual(history[self.sprint_2.id]["planned_days"], 2)
        self.assertEqual(history[self.sprint_2.id]["run_days"], 0)

    def test_dashboard_partners(self):
        partner_ids = [
            p["id"]
            for p in self.env["project.sprint"].get_sprint_dashboard_data()["partners"]
        ]
        self.assertIn(self.customer.id, partner_ids)
        self.assertIn(self.other_customer.id, partner_ids)

    def test_action_open_sprint_dashboard(self):
        action = self.project.action_open_sprint_dashboard()
        self.assertEqual(action["tag"], "project_sprint_dashboard.sprint_dashboard")
        self.assertEqual(action["params"]["partner_id"], self.customer.id)

    def test_run_task_without_sprint_goes_to_closing_sprint(self):
        self.project.run_tag_ids = self.bug_tag
        task = self.env["project.task"].create(
            {
                "name": "Bug",
                "project_id": self.project.id,
                "tag_ids": [(6, 0, self.bug_tag.ids)],
                "estimate_step_id": self.step.id,
            }
        )
        self.assertTrue(task.is_run)
        self.assertFalse(task.sprint_id)
        task.state = "1_done"
        self.assertEqual(task.sprint_id, self.sprint_2)
        self.assertEqual(task.sprint_history_ids, self.sprint_2)
        data = self._get_data(self.sprint_2)
        self.assertEqual(data["totals"]["done"]["count"], 1)
        self.assertEqual(data["totals"]["run"]["count"], 1)
        self.assertEqual(data["totals"]["run"]["days"], 2)

    def test_open_run_task_without_sprint_stays_out(self):
        self.project.run_tag_ids = self.bug_tag
        task = self.env["project.task"].create(
            {
                "name": "Bug",
                "project_id": self.project.id,
                "tag_ids": [(6, 0, self.bug_tag.ids)],
            }
        )
        self.assertFalse(task.sprint_id)
        self.assertEqual(self._get_data(self.sprint_2)["totals"]["run"]["count"], 0)

    def test_run_task_in_sprint_keeps_its_sprint(self):
        self.project.run_tag_ids = self.bug_tag
        run_task = self._create_task(
            self.sprint_1,
            estimate_step_id=self.step.id,
            tag_ids=[(6, 0, self.bug_tag.ids)],
            state="1_done",
        )
        self._create_task(self.sprint_1, estimate_step_id=self.step.id)
        self.assertEqual(run_task.sprint_id, self.sprint_1)
        data = self._get_data(self.sprint_1)
        self.assertEqual(data["totals"]["run"]["count"], 1)
        self.assertEqual(data["totals"]["run"]["done_days"], 2)
        project_data = data["projects"][0]
        self.assertEqual(project_data["count"], 2)
        self.assertEqual(project_data["buckets"]["run"]["count"], 1)
        history = {h["id"]: h for h in data["history"]}
        self.assertEqual(history[self.sprint_1.id]["run_days"], 2)
        self.assertEqual(history[self.sprint_1.id]["planned_days"], 4)

    def test_tag_not_run_on_project(self):
        task = self.env["project.task"].create(
            {
                "name": "Bug",
                "project_id": self.project.id,
                "tag_ids": [(6, 0, self.bug_tag.ids)],
            }
        )
        self.assertFalse(task.is_run)
        task.state = "1_done"
        self.assertFalse(task.sprint_id)
        self.project.run_tag_ids = self.bug_tag
        self.assertTrue(task.is_run)
