# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo.tests import SavepointCase


class TestWorkload(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.my_project = cls.env["project.project"].create(
            {
                "name": "My Project",
                "use_workload": True,
            }
        )
        cls.user = cls.env.ref("base.demo_user0")
        cls.my_project_filter = cls.env["ir.filters"].create(
            {
                "name": "My project Filter",
                "domain": [("id", "=", cls.my_project.id)],
                "model_id": "project.project",
            }
        )
        cls.capacity = cls.env["project.user.capacity"].create(
            {
                "name": "My Capacity for my project",
                "user_id": cls.user.id,
                "filter_id": cls.my_project_filter.id,
                "line_ids": [
                    (0, 0, {"hours": 21}),
                ],
            }
        )

    def test_create_capacity(self):
        self.assertEqual(len(self.capacity.unit_ids), 52)
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

    def test_assign_user(self):
        pass

    def test_assign_date(self):
        pass

    def test_change_user(self):
        pass

    def test_change_date(self):
        pass
