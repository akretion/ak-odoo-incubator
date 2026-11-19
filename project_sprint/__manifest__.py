# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Sprint",
    "summary": "Manage your projects tasks in a varying granularity",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "maintainers": ["paradoxxxzero"],
    "author": " Akretion",
    "license": "AGPL-3",
    "depends": ["project"],
    "data": [
        "security/ir.model.access.csv",
        "security/project_sprint_security.xml",
        "views/project_sprint_view.xml",
        "views/project_task_view.xml",
        "views/project_project_view.xml",
    ],
}
