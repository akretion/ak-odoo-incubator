# Copyright 2026 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    env["project.task"].with_context(active_test=False).search(
        [("sprint_level_4_id", "!=", False)]
    )._update_sprint_history()
