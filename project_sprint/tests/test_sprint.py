# Copyright 2025 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.project_sprint.tests.common import TestSprintCommon


class TestSprint(TestSprintCommon):
    def _create_sprint(self, year=2025):
        root = self.env["project.sprint"].create(
            {
                "name": str(year),
            }
        )
        root.action_generate()
        return root

    def _create_task(self):
        return self.env["project.task"].create(
            {
                "name": "Task 1",
                "project_id": self.project.id,
                "user_ids": [(4, self.user_1.id)],
            }
        )

    def test_generate_sprint(self):
        self.assertFalse(self.env["project.sprint"].search([]))
        self._create_sprint()
        top_level = self.env["project.sprint"].search([("level", "=", 1)])
        self.assertEqual(len(top_level), 1)
        self.assertEqual(top_level.name, "2025")
        self.assertEqual(len(top_level.child_ids), 4)
        self.assertEqual(top_level.child_ids.mapped("name"), ["Q1", "Q2", "Q3", "Q4"])

        quarters = self.env["project.sprint"].search([("level", "=", 2)])
        self.assertEqual(len(quarters), 4)
        self.assertEqual(quarters, top_level.child_ids)
        self.assertEqual(quarters.mapped(lambda q: len(q.child_ids)), [3] * 4)

        months = self.env["project.sprint"].search([("level", "=", 3)])
        self.assertEqual(len(months), 12)
        self.assertEqual(months, quarters.child_ids)
        self.assertEqual(months.mapped(lambda m: len(m.child_ids)), [2] * 12)

        fortnights = self.env["project.sprint"].search([("level", "=", 4)])
        self.assertEqual(len(fortnights), 24)
        self.assertEqual(fortnights, months.child_ids)

    def test_generate_sprint_unusual_year(self):
        self.assertFalse(self.env["project.sprint"].search([]))
        self._create_sprint(2000)
        top_level = self.env["project.sprint"].search([("level", "=", 1)])
        self.assertEqual(len(top_level), 1)
        self.assertEqual(top_level.name, "2000")
        self.assertEqual(len(top_level.child_ids), 4)
        self.assertEqual(top_level.child_ids.mapped("name"), ["Q1", "Q2", "Q3", "Q4"])

        quarters = self.env["project.sprint"].search([("level", "=", 2)])
        self.assertEqual(len(quarters), 4)
        self.assertEqual(quarters, top_level.child_ids)
        self.assertEqual(quarters.mapped(lambda q: len(q.child_ids)), [3] * 4)

        months = self.env["project.sprint"].search([("level", "=", 3)])
        self.assertEqual(len(months), 12)
        self.assertEqual(months, quarters.child_ids)
        self.assertEqual(months.mapped(lambda m: len(m.child_ids)), [2] * 12)

        fortnights = self.env["project.sprint"].search([("level", "=", 4)])
        self.assertEqual(len(fortnights), 24)
        self.assertEqual(fortnights, months.child_ids)

    def test_task_in_sprint(self):
        self._create_sprint()
        task = self._create_task()
        task.sprint_id = self.env["project.sprint"].search([("level", "=", 3)])[0]
        task._compute_planned_date_start_end_from_sprint()
        self.assertEqual(task.planned_date_start.date(), task.sprint_id.date_start)
        self.assertEqual(task.planned_date_end.date(), task.sprint_id.date_end)
        self.assertEqual(task.sprint_level_1_id, task.sprint_id.parent_id.parent_id)
        self.assertEqual(task.sprint_level_2_id, task.sprint_id.parent_id)
        self.assertEqual(task.sprint_level_3_id, task.sprint_id)
        self.assertFalse(task.sprint_level_4_id)
