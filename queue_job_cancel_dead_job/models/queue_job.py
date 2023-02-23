# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from datetime import datetime, timedelta

from odoo import models
from odoo.tools import config


class QueueJob(models.Model):
    _inherit = "queue.job"

    def _cancel_dead_job(self):
        # search dead job based on worker life duration and cancel them
        dead_start_date = datetime.now() - timedelta(
            seconds=config.get("limit_time_real")
        )
        jobs = self.search(
            [("state", "=", "started"), ("date_enqueued", "<", dead_start_date)]
        )
        jobs.write({"state": "failed", "result": "dead job"})
