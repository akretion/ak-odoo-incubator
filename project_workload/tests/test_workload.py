# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo.addons.project_workload.tests.common import TestWorkloadCommon


class TestWorkload(TestWorkloadCommon):
    def test_task_assign_with_hours(self):
        workload = self.task.workload_ids
        self.assertEqual(len(workload), 1)
        self.assertEqual(workload.date_start, self.task.date_start.date())
        self.assertEqual(workload.date_end, self.task.date_end.date())
        self.assertEqual(workload.hours, 21)
        load_unit = workload.unit_ids
        self.assertEqual(len(load_unit), 3)
        self.assertEqual(load_unit.user_id, self.user_1)
        self.assertEqual(set(load_unit.mapped("hours")), {7})

    def test_change_user(self):
        self.task.user_id = self.user_2
        self.assertEqual(self.task.workload_ids.user_id, self.user_2)
        self.assertEqual(self.task.workload_ids.unit_ids.user_id, self.user_2)

    def test_remove_user(self):
        self.task.user_id = self.user_2
        self.assertTrue(self.task.workload_ids)
        self.task.user_id = False
        self.assertFalse(self.task.workload_ids)

    def test_change_date(self):
        self.task.date_end = self.task.date_start + timedelta(days=13)
        workload = self.task.workload_ids
        self.assertEqual(len(workload), 1)
        self.assertEqual(workload.date_start, self.task.date_start.date())
        self.assertEqual(workload.date_end, self.task.date_end.date())
        self.assertEqual(workload.hours, 21)
        load_unit = workload.unit_ids
        self.assertEqual(len(load_unit), 2)
        self.assertEqual(load_unit.user_id, self.user_1)
        self.assertEqual(set(load_unit.mapped("hours")), {10.5})
