# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.addons.project_workload.tests.common import TestWorkloadCommon


class TestWorkload(TestWorkloadCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.task_management, cls.task_review = cls.env["project.task"].create(
            [
                {"name": "Management", "project_id": cls.project.id},
                {"name": "Review", "project_id": cls.project.id},
            ]
        )
        cls.type_management, cls.type_review = cls.env[
            "project.task.workload.addition.type"
        ].create(
            [
                {"name": "Management", "default_percentage": 15},
                {"name": "Review", "default_percentage": 20},
            ]
        )
        cls.add_work_management, cls.add_work_review = cls.env[
            "project.task.workload.addition"
        ].create(
            [
                {
                    "project_id": cls.project.id,
                    "type_id": cls.type_management.id,
                    "user_id": cls.user_1.id,
                    "task_id": cls.task_management.id,
                },
                {
                    "project_id": cls.project.id,
                    "type_id": cls.type_review.id,
                    "user_id": cls.user_2.id,
                    "task_id": cls.task_review.id,
                },
            ]
        )

    def _create_task(self, user_ids=None):
        now = datetime.now()
        return self.env["project.task"].create(
            {
                "name": "Task 1",
                "project_id": self.project.id,
                "user_ids": [(6, 0, user_ids.ids)] if user_ids else [],
                "planned_date_start": now,
                "planned_date_end": now + timedelta(days=20),
                "planned_hours": 21,
            }
        )

    def test_task_assign_with_hours(self):
        task = self._create_task(self.user_1)
        workloads = task.workload_ids

        self.assertEqual(len(workloads), 3)
        workload, workload_management, workload_review = workloads

        self.assertEqual(workload.date_start, task.planned_date_start.date())
        self.assertEqual(workload.date_end, task.planned_date_end.date())
        self.assertEqual(workload.user_id, self.user_1)
        self.assertFalse(workload.additional_workload_id)

        self.assertEqual(workload_management.date_start, task.planned_date_start.date())
        self.assertEqual(workload_management.date_end, task.planned_date_end.date())
        self.assertEqual(workload_management.hours, 3.15)
        self.assertEqual(workload_management.user_id, self.user_1)
        self.assertEqual(
            workload_management.additional_workload_id, self.add_work_management
        )

        self.assertEqual(workload_review.date_start, task.planned_date_start.date())
        self.assertEqual(workload_review.date_end, task.planned_date_end.date())
        self.assertEqual(workload_review.hours, 4.2)
        self.assertEqual(workload_review.user_id, self.user_2)
        self.assertEqual(workload_review.additional_workload_id, self.add_work_review)

    def _assert_only_additionnal_workload(self, workloads):
        self.assertEqual(len(workloads), 2)
        workload_management, workload_review = workloads
        self.assertEqual(
            workload_management.additional_workload_id, self.add_work_management
        )
        self.assertEqual(workload_review.additional_workload_id, self.add_work_review)

    def test_create_unasign_task(self):
        task = self._create_task()
        self._assert_only_additionnal_workload(task.workload_ids)

    def test_remove_user(self):
        task = self._create_task(self.user_1)
        task.user_ids = [(5, 0, 0)]
        self._assert_only_additionnal_workload(task.workload_ids)

    def test_update_hours(self):
        task = self._create_task(self.user_1)
        task.planned_hours = 42
        self.assertEqual(len(task.workload_ids), 3)
        workload, workload_management, workload_review = task.workload_ids
        self.assertEqual(workload_management.hours, 6.30)
        self.assertEqual(workload_review.hours, 8.4)

    def test_task_assign_with_hours_and_multiple_users(self):
        task = self._create_task(self.user_1 | self.user_2)
        workloads = task.workload_ids

        self.assertEqual(len(workloads), 4)
        (
            workload_user_1,
            workload_user_2,
            workload_management_user_1,
            workload_review_user_2,
        ) = workloads

        self.assertEqual(workload_user_1.date_start, task.planned_date_start.date())
        self.assertEqual(workload_user_1.date_end, task.planned_date_end.date())
        self.assertEqual(workload_user_1.user_id, self.user_1)
        self.assertFalse(workload_user_1.additional_workload_id)

        self.assertEqual(workload_user_2.date_start, task.planned_date_start.date())
        self.assertEqual(workload_user_2.date_end, task.planned_date_end.date())
        self.assertEqual(workload_user_2.user_id, self.user_2)
        self.assertFalse(workload_user_2.additional_workload_id)

        self.assertEqual(
            workload_management_user_1.date_start, task.planned_date_start.date()
        )
        self.assertEqual(
            workload_management_user_1.date_end, task.planned_date_end.date()
        )
        self.assertEqual(workload_management_user_1.hours, 3.15)
        self.assertEqual(workload_management_user_1.user_id, self.user_1)
        self.assertEqual(
            workload_management_user_1.additional_workload_id, self.add_work_management
        )

        self.assertEqual(
            workload_review_user_2.date_start, task.planned_date_start.date()
        )
        self.assertEqual(workload_review_user_2.date_end, task.planned_date_end.date())
        self.assertEqual(workload_review_user_2.hours, 4.2)
        self.assertEqual(workload_review_user_2.user_id, self.user_2)
        self.assertEqual(
            workload_review_user_2.additional_workload_id, self.add_work_review
        )
