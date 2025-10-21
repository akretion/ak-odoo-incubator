# Copyright 2025 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

from ..routers import gitlab_router

_logger = logging.getLogger(__name__)


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("gitlab", "Gitlab endpoint")],
        ondelete={"gitlab": "cascade"},
    )
    gitlab_token: str = fields.Char(
        string="Gitlab Token", help="Token used to authenticate Gitlab webhooks"
    )

    def _get_fastapi_routers(self):
        routers = super()._get_fastapi_routers()
        if self.app == "gitlab":
            return routers + [gitlab_router]
        return routers
