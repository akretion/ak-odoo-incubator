# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Workload",
    "summary": "Ressource Workload Management",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "depends": [
        "project_timeline",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_task_workload_view.xml",
        "views/project_task_view.xml",
        "views/project_project_view.xml",
        "views/menu_view.xml",
    ],
}
