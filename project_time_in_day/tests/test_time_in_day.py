# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProjectUomDays(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Récupération des UoM de base
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.uom_categ_wtime = cls.env.ref("uom.uom_categ_wtime")

        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project UoM",
                "allow_timesheets": True,
            }
        )

        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
                "allocated_hours": 16.0,
            }
        )

        cls.env["account.analytic.line"].create(
            {
                "name": "Work 8h",
                "project_id": cls.project.id,
                "task_id": cls.task.id,
                "unit_amount": 8.0,
                "employee_id": cls.env.user.employee_id.id
                or cls.env["hr.employee"].create({"name": "Test Employee"}).id,
            }
        )

    def test_01_default_uom_conversion(self):
        # Allocated: 16h / 8h = 2 days
        # Effective: 8h / 8h = 1 day
        # Remaining: 8h / 8h = 1 day
        self.assertEqual(
            self.task.allocated_days, 2.0, "Allocated days should be 2.0 (16h/8h)"
        )
        self.assertEqual(
            self.task.effective_days, 1.0, "Effective days should be 1.0 (8h/8h)"
        )
        self.assertEqual(
            self.task.remaining_days, 1.0, "Remaining days should be 1.0 (8h/8h)"
        )

    def test_02_custom_uom_conversion(self):
        uom_7h = self.env["uom.uom"].create(
            {
                "name": "7 Hours",
                "category_id": self.uom_categ_wtime.id,
                "uom_type": "smaller",
                "factor": 7,
            }
        )
        self.project.hour_uom_id = uom_7h
        # Allocated: 16h / 7h ≈ 2.2857... -> 2.29
        # Effective: 8h / 7h ≈ 1.1428... -> 1.14
        # Remaining: 8h / 7h ≈ 1.14

        self.assertAlmostEqual(self.task.allocated_days, 2.29, places=2)
        self.assertAlmostEqual(self.task.effective_days, 1.14, places=2)
        self.assertAlmostEqual(self.task.remaining_days, 1.14, places=2)
