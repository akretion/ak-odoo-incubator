# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo.tests import SavepointCase


@freeze_time("2023-07-24")
class TestWorkload(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create(
            {
                "name": "Project 1",
                "use_workload": True,
            }
        )
        cls.user_1 = cls.env.ref("base.demo_user0")
        cls.user_2 = cls.env.ref("base.user_demo")
        cls.project_filter = cls.env["ir.filters"].create(
            {
                "name": "Project Filter 1",
                "domain": [("id", "=", cls.project.id)],
                "model_id": "project.project",
            }
        )
        cls.capacity = cls.env["project.user.capacity"].create(
            {
                "name": "My Capacity for project 1",
                "user_id": cls.user_1.id,
                "filter_id": cls.project_filter.id,
                "line_ids": [
                    (0, 0, {"hours": 21}),
                ],
            }
        )
        now = datetime.now()
        cls.task = cls.env["project.task"].create(
            {
                "name": "Task 1",
                "project_id": cls.project.id,
                "user_id": cls.user_1.id,
                "date_start": now,
                "date_end": now + timedelta(days=20),
                "planned_hours": 21,
            }
        )

    def test_create_capacity(self):
        self.assertEqual(len(self.capacity.unit_ids), 52)
        self.assertEqual(set(self.capacity.unit_ids.mapped("hours")), {21})

    def test_cron_create_capacity(self):
        self.env["project.user.capacity"]._cron_generate_week_report(60)
        self.assertEqual(len(self.capacity.unit_ids), 60)
        self.assertEqual(set(self.capacity.unit_ids.mapped("hours")), {21})

    def test_change_capacity_hours(self):
        self.capacity.line_ids.hours = 28
        self.assertEqual(set(self.capacity.unit_ids.mapped("hours")), {28})

    def test_capacity_modulo(self):
        self.capacity.line_ids.modulo = 3
        for idx, unit in enumerate(self.capacity.unit_ids.sorted()):
            if idx % 3:
                self.assertEqual(unit.hours, 0)
            else:
                self.assertEqual(unit.hours, 21)

    def test_capacity_date_start_end(self):
        self.capacity.line_ids.date_end = datetime.now() + timedelta(days=70)
        for idx, unit in enumerate(self.capacity.unit_ids.sorted()):
            if idx <= 10:
                self.assertEqual(unit.hours, 21)
            else:
                self.assertEqual(unit.hours, 0)

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

    def test_generate_report(self):
        report = self.env["project.load.report"].create({})
        report._generate_lines()
        for line in report.line_ids:
            self.assertEqual(line.user_id, self.user_1)
            if line.week in ["2023-30", "2023-31", "2023-32"]:
                self.assertEqual(line.total_planned_hours, 7)
                self.assertEqual(line.project_planned_hours, 7)
            else:
                self.assertEqual(line.total_planned_hours, 0)
                self.assertEqual(line.project_planned_hours, 0)
            self.assertEqual(line.total_capacity_hours, 21)
            self.assertEqual(line.project_capacity_hours, 21)
