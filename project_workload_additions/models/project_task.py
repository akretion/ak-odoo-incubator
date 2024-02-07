# Copyright 2024 Akretion (https://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _get_new_workloads(self):
        rv = super()._get_new_workloads()
        # super creates a new workload if there are none
        # but here we can have only additional workloads
        # so we also need to check if the existing workloads are additional
        if not rv and all(
            workload.additional_workload_id for workload in self.workload_ids
        ):
            rv.append(self._prepare_workload())

        additional_workloads = {
            workload.additional_workload_id: workload
            for workload in self.workload_ids
            if workload.additional_workload_id
        }
        # Now we need to create a new workload for each additional workload
        for additional_workload in self.project_id.additional_workload_ids:
            if additional_workload not in additional_workloads:
                rv.append(self._prepare_additional_workload(additional_workload))

        return rv

    def _get_updated_workloads(self):
        # We sort the workloads by additional_workload_id to ensure that the first workload is the main one
        self.workload_ids = self.workload_ids.sorted(
            key=lambda w: w.additional_workload_id
        )
        rv = super()._get_updated_workloads()
        if rv and rv[0][0].additional_workload_id:
            rv = []

        additional_workloads = {
            workload.additional_workload_id: workload
            for workload in self.workload_ids
            if workload.additional_workload_id
        }
        # Now we need to update the existing workload for each additional workload
        for additional_workload, workload in additional_workloads.items():
            rv.append(
                (
                    workload,
                    self._prepare_additional_workload(additional_workload),
                )
            )

        return rv

    def _get_obsolete_workloads(self):
        self.workload_ids = self.workload_ids.sorted(
            key=lambda w: w.additional_workload_id
        )
        rv = super()._get_obsolete_workloads()
        if rv:
            # Do not delete additional workloads
            rv = [workload for workload in rv if not workload.additional_workload_id]

        # Remove all additional workloads that are not in the project anymore
        additional_workloads = {
            workload.additional_workload_id: workload
            for workload in self.workload_ids
            if workload.additional_workload_id
        }
        for additional_workload in additional_workloads:
            if additional_workload not in self.project_id.additional_workload_ids:
                rv.append(additional_workload)
        return rv

    def _prepare_additional_workload(self, additional_workload, **extra):
        return self._prepare_workload(
            additional_workload_id=additional_workload.id,
            hours=additional_workload._compute_hours_from_task(self),
            user_id=additional_workload.user_id.id,
            **extra,
        )
