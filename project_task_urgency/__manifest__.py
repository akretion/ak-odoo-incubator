# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Project Task Urgency",
    "version": "18.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "summary": "Add urgency to project tasks",
    "category": "Project Management",
    "depends": ["project"],
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "data": [
        "data/mail_activity_data.xml",
        "views/project_views.xml",
        "views/project_task_views.xml",
    ],
    "maintainers": ["paradoxxxzero"],
    "demo": [],
    "installable": True,
    "license": "AGPL-3",
}
