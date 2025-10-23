# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Gitlab Integration",
    "version": "16.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "summary": "Integration with Gitlab for project management",
    "category": "Tools",
    "depends": [
        "project",
        "mail",
        "fastapi",
        "queue_job",
    ],
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "data": [
        "security/res_groups.xml",
        "security/res_users.xml",
        "security/ir_model_access.xml",
        "views/gitlab_merge_request_views.xml",
        "views/project_task_views.xml",
        "views/fastapi_endpoint_views.xml",
        "wizards/gitlab_sync_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "gitlab_integration/static/src/**/*",
        ],
    },
    "maintainers": ["paradoxxxzero"],
    "demo": [],
    "installable": True,
    "license": "AGPL-3",
}
