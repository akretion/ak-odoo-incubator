# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.addons.project_workload.tests.common import TestWorkloadCommon


class TestWorkload(TestWorkloadCommon):
    def _create_task(self):
        now = datetime.now()
        self.task = self.env["project.task"].create(
            {
                "name": "Task 1",
                "project_id": self.project.id,
                "user_ids": [(4, self.user_1.id)],
                "planned_date_start": now,
                "planned_date_end": now + timedelta(days=20),
                "planned_hours": 21,
            }
        )

    def test_task_assign_with_hours(self):
        self._create_task()
        workload = self.task.workload_ids
        self.assertEqual(len(workload), 1)
        self.assertEqual(workload.date_start, self.task.planned_date_start.date())
        self.assertEqual(workload.date_end, self.task.planned_date_end.date())
        self.assertEqual(workload.hours, 21)
        load_unit = workload.unit_ids
        self.assertEqual(len(load_unit), 3)
        self.assertEqual(load_unit.user_id, self.user_1)
        self.assertEqual(set(load_unit.mapped("hours")), {7})

    def test_change_user(self):
        self._create_task()
        self.task.user_ids = [(6, 0, [self.user_2.id])]
        self.assertEqual(self.task.workload_ids.user_id, self.user_2)
        self.assertEqual(self.task.workload_ids.unit_ids.user_id, self.user_2)

    def test_add_user(self):
        self._create_task()
        self.task.user_ids = [(4, self.user_2.id)]
        self.assertEqual(len(self.task.workload_ids), 2)
        self.assertEqual(
            self.task.workload_ids.mapped("user_id"), self.user_1 + self.user_2
        )
        self.assertEqual(
            self.task.workload_ids.unit_ids.mapped("user_id"), self.user_1 + self.user_2
        )

    def test_remove_user(self):
        self._create_task()
        self.task.user_ids = [(5, 0, 0)]
        self.assertFalse(self.task.workload_ids)

    def test_change_date(self):
        self._create_task()
        self.task.planned_date_end = self.task.planned_date_start + timedelta(days=13)
        workload = self.task.workload_ids
        self.assertEqual(len(workload), 1)
        self.assertEqual(workload.date_start, self.task.planned_date_start.date())
        self.assertEqual(workload.date_end, self.task.planned_date_end.date())
        self.assertEqual(workload.hours, 21)
        load_unit = workload.unit_ids
        self.assertEqual(len(load_unit), 2)
        self.assertEqual(load_unit.user_id, self.user_1)
        self.assertEqual(set(load_unit.mapped("hours")), {10.5})
