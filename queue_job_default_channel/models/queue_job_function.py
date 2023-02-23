# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class QueueJobFunction(models.Model):
    _inherit = "queue.job.function"

    def job_default_config(self):
        config = super().job_default_config()
        return config._replace(channel="root.default.basic_job")
