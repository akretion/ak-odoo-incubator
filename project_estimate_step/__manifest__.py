# Copyright 2022 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Estimate Step",
    "summary": "Add step estimation for project",
    "version": "12.0.1.0.0",
    "development_status": "Alpha",
    "category": "Project",
    "website": "www.akretion.com",
    "author": " Akretion",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "project",
        "hr_timesheet",
    ],
    "data": [
        "views/project_project_view.xml",
        "views/project_task_view.xml",
        "views/project_task_type_view.xml",
        "views/project_estimate_step_view.xml",
        "security/ir.model.access.csv",
    ],
    "demo": [
    ],
}
