# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _get_main_workloads(self):
        return (
            super()
            ._get_main_workloads()
            .filtered(lambda s: not s.additional_workload_id)
        )

    def _get_new_workloads(self):
        rv = super()._get_new_workloads()
        # We need to create a new workload for each additional workload
        for additional_workload in self.project_id.additional_workload_ids:
            if additional_workload not in self.workload_ids.additional_workload_id:
                rv.append(self._prepare_additional_workload(additional_workload))
        return rv

    def _get_updated_workloads(self):
        rv = super()._get_updated_workloads()
        for workload in self.workload_ids:
            additional_workload = workload.additional_workload_id
            if additional_workload in self.project_id.additional_workload_ids:
                rv.append(
                    (workload, self._prepare_additional_workload(additional_workload))
                )
        return rv

    def _get_obsolete_workloads(self):
        rv = super()._get_obsolete_workloads()
        for workload in self.workload_ids:
            additional_workload = workload.additional_workload_id
            if additional_workload and (
                additional_workload not in self.project_id.additional_workload_ids
                or additional_workload.user_id not in self.user_ids
            ):
                rv.append(additional_workload)
        return rv

    def _prepare_additional_workload(self, additional_workload, **extra):
        return self._prepare_workload(
            additional_workload.user_id,
            additional_workload_id=additional_workload.id,
            hours=additional_workload._compute_hours_from_task(self),
            **extra,
        )
