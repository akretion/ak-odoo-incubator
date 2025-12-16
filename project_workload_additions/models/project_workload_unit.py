# Copyright 2024 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class ProjectWorkloadUnit(models.Model):
    _inherit = "project.workload.unit"

    def name_get(self):
        result = super().name_get()
        units_names = dict(result)
        for unit_id, name in result:
            unit = self.browse(unit_id)
            if unit.workload_id.additional_workload_id:
                name = f"{unit.workload_id.additional_workload_id.task_id.name} "
                f"{_('of')} {name}"
                units_names[unit_id] = name

        return list(units_names.items())
