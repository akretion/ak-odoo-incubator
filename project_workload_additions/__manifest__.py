# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Workload Additions",
    "summary": "Automatically add extra load to tasks.",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "depends": [
        "project_workload",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_project_view.xml",
        "views/project_task_view.xml",
        "views/project_task_workload_addition_type_views.xml",
        "views/project_task_workload_view.xml",
        "views/menu_view.xml",
    ],
}
