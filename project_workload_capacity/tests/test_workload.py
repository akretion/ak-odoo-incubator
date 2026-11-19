# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.addons.project_workload.tests.common import TestWorkloadCommon


class TestWorkloadCapacity(TestWorkloadCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

    def test_generate_report(self):
        report = self.env["project.load.capacity.report"].create({})
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
