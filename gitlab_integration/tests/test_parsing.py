# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import BaseCase

from ..models.gitlab_merge_request import extract_task_ids_from_title


class TestParsing(BaseCase):
    def test_extract_task_ids_from_title_1(self):
        title = "[123] Implement feature [X]"
        task_ids = extract_task_ids_from_title(title)
        self.assertEqual(task_ids, [123])

    def test_extract_task_ids_from_title_2(self):
        title = "[1][2] [3]Implement feature [4] X"
        task_ids = extract_task_ids_from_title(title)
        self.assertEqual(task_ids, [1, 2, 3])

    def test_extract_task_ids_from_title_3(self):
        title = " [123] [456,789] Implement feature X"
        task_ids = extract_task_ids_from_title(title)
        self.assertEqual(task_ids, [123, 456789])

    def test_extract_task_ids_from_title_4(self):
        title = "[abc] [456] Implement feature X"
        task_ids = extract_task_ids_from_title(title)
        self.assertEqual(task_ids, [])

    def test_extract_task_ids_from_title_5(self):
        title = "Draft: [456] Implement feature X"
        task_ids = extract_task_ids_from_title(title)
        self.assertEqual(task_ids, [456])

    def test_extract_task_ids_from_title_6(self):
        title = " [123 456 78,9] Implement feature X"
        task_ids = extract_task_ids_from_title(title)
        self.assertEqual(task_ids, [123456789])

    def test_extract_task_ids_from_title_7(self):
        title_no_tasks = "Implement feature Y"
        task_ids_no_tasks = extract_task_ids_from_title(title_no_tasks)
        self.assertEqual(task_ids_no_tasks, [])
