# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Sprint Dashboard",
    "summary": "Sprint dashboard per customer: done, in progress, to start, "
    "carried over, run",
    "version": "18.0.1.0.0",
    "development_status": "Beta",
    "category": "Project",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": "Akretion",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "depends": [
        "project_sprint",
        "project_task_stage_state",
        "project_estimate_step",
    ],
    "data": [
        "views/project_task.xml",
        "views/project_project.xml",
        "views/sprint_dashboard.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "project_sprint_dashboard/static/src/sprint_dashboard/*",
        ],
    },
    "post_init_hook": "post_init_hook",
    "installable": True,
}
