# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Queue Job Default Channel",
    "summary": "Default channel for queue job",
    "version": "14.0.1.0.0",
    "development_status": "Alpha",
    "category": "Job",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "queue_job",
    ],
    "data": [
        "data/queue_job_channel_data.xml",
    ],
    "demo": [],
}
