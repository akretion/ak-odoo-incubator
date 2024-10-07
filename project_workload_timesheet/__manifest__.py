# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Project Workload Timesheet",
    "summary": "Add Workload To Timesheets",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "depends": [
        "project_workload",
        "hr_timesheet_sheet",
    ],
    "data": [
        "views/hr_timesheet_sheet_views.xml",
    ],
}