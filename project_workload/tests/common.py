# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo.tests import SavepointCase


@freeze_time("2023-07-24")
class TestWorkloadCommon(SavepointCase):
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
