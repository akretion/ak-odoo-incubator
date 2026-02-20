# Copyright 2024 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models

from ..http import FastapiRootPaths


class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    @api.model
    def _update_root_paths_registry(self):
        root_paths = self.env["fastapi.endpoint"].search([]).mapped("root_path")
        FastapiRootPaths.set_root_paths(self.env.cr.dbname, root_paths)

    def _register_hook(self):
        super()._register_hook()
        self._update_root_paths_registry()

    def _inverse_root_path(self):
        super()._inverse_root_path()
        self._update_root_paths_registry()

    @api.depends("root_path")
    def _compute_urls(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        for rec in self:
            rec.docs_url = f"{base_url}{rec.root_path}/docs"
            rec.redoc_url = f"{base_url}{rec.root_path}/redoc"
            rec.openapi_url = f"{base_url}{rec.root_path}/openapi.json"
