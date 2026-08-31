# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from contextlib import closing, contextmanager
from logging import getLogger
from urllib.parse import urlparse

from odoo import SUPERUSER_ID, api, fields, models
from odoo.exceptions import AccessDenied, ValidationError
from odoo.modules.registry import Registry
from odoo.service.db import (
    DatabaseExists,
    _create_empty_database,
    _initialize_db,
    exp_drop,
    exp_rename,
    list_dbs,
)
from odoo.sql_db import close_db
from odoo.tools import config

_logger = getLogger(__name__)

# Allow db functions without list_db config
db_rename = exp_rename.__wrapped__
db_drop = exp_drop.__wrapped__


class ResPartnerInstance(models.Model):
    _name = "res.partner.instance"
    _rec_name = "subdomain"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("live", "Live"),
            ("archived", "Archived"),
        ],
        compute="_compute_state",
    )
    partner_id = fields.Many2one("res.partner", required=True)
    subdomain = fields.Char(
        compute="_compute_subdomain",
        store=True,
        precompute=True,
        required=True,
        readonly=False,
    )
    db_name = fields.Char(
        compute="_compute_db_name",
        store=True,
        readonly=True,
    )
    url = fields.Char(
        compute="_compute_url",
        readonly=True,
    )

    _sql_constraints = [
        ("subdomain_unique", "UNIQUE(subdomain)", "Subdomain must be unique"),
    ]

    @api.constrains("subdomain")
    def _check_subdomain(self):
        for record in self:
            if re.compile(
                config["dbfilter"].replace("%d", re.escape(record.subdomain))
            ).match(self.env.cr.dbname):
                raise ValidationError(
                    self.env._("Subdomain cannot be the same as the master domain")
                )

    @property
    def master_instance(self):
        master = config.get("partner_db_instance_master")
        if not master:
            raise ValueError("partner_db_instance_master is not configured")
        return master

    @property
    def instance_admin_password(self):
        instance_admin_password = config.get("partner_db_instance_password")
        if not instance_admin_password:
            raise ValueError("partner_db_instance_password is not configured")
        return instance_admin_password

    @property
    def archived_db_name(self):
        return f"_archived_{self.db_name}"

    @api.depends("subdomain")
    def _compute_url(self):
        for instance in self:
            instance.url = None
            if instance.subdomain:
                base_url = (
                    self.env["ir.config_parameter"].sudo().get_param("web.base.url")
                )
                if not base_url:
                    _logger.warning("No base URL set, cannot compute instance URL")
                    continue

                url = urlparse(base_url)
                instance_netloc = url.netloc.replace(
                    url.netloc.split(".")[0], instance.subdomain
                )
                url = url._replace(netloc=instance_netloc)
                instance.url = url.geturl()

    def _clean_partner_name(self):
        if not self.partner_id:
            return ""
        name = self.partner_id.name
        return re.sub(r"[^a-zA-Z0-9-]", "-", name).lower()

    @api.depends("partner_id")
    def _compute_subdomain(self):
        for record in self:
            record.subdomain = record._clean_partner_name()

    def _compute_state(self):
        dbs = list_dbs(True)
        for record in self:
            if record.archived_db_name in dbs:
                record.state = "archived"
            elif record.db_name in dbs:
                record.state = "live"
            else:
                record.state = "draft"

    @api.depends("partner_id")
    def _compute_db_name(self):
        for record in self:
            base = self.master_instance.split("_")[0]
            if not record.db_name or record.state == "draft":
                record.db_name = f"{base}_{record._clean_partner_name()}"

    def action_deploy(self):
        for record in self:
            record._setup_database()

    def action_archive(self):
        for record in self:
            close_db(record.db_name)
            db_rename(record.db_name, record.archived_db_name)

    def action_unarchive(self):
        for record in self:
            db_rename(record.archived_db_name, record.db_name)

    def action_delete(self):
        for record in self:
            db_drop(record.archived_db_name)

    @contextmanager
    def instance_env(self):
        registry = Registry.new(self.db_name, False, None, update_module=True)
        with closing(registry.cursor()) as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            try:
                yield env
            except Exception:
                cr.rollback()
                raise
            else:
                cr.commit()  # pylint: disable=invalid-commit

    def action_connect(self):
        self.ensure_one()
        master_user = self.env.user

        if not master_user.has_group(
            "partner_db_instance.group_partner_instance_manager"
        ):
            raise AccessDenied()

        with self.instance_env() as env:
            user = env["res.users"].search([("login", "=", master_user.login)])
            if not user:
                user = env["res.users"].create(
                    {"login": master_user.login, "name": master_user.name}
                )
            token = user._get_instance_db_jwt_token()
            user_id = user.id

        return {
            "type": "ir.actions.act_url",
            "url": f"{self.url}/web/instance/{user_id}/{token}/connect",
            "target": "new",
        }

    def _setup_database(self):
        self.ensure_one()
        if self.master_instance != self.env.cr.dbname:
            raise ValueError(
                f"Cannot setup database for instance {self.db_name} "
                "as it is not the master instance"
            )
        instance_admin_password = self.instance_admin_password
        login = f"admin_{self.db_name}"

        db_name = self.db_name
        try:
            _create_empty_database(db_name)
        except DatabaseExists:
            _logger.warning(f"Database {db_name} already exists")
            return

        _initialize_db(
            None,
            db_name,
            False,
            self.env.company.partner_id.lang,
            instance_admin_password,
            login,
            self.env.company.country_id.code,
            self.env.company.phone,
        )
        modules_to_install = (
            config.get("partner_db_instance_modules") or "db_instance"
        ).split(",")

        with self.instance_env() as env:
            modules = env["ir.module.module"].search(
                [("name", "in", modules_to_install)]
            )
            if len(modules) < len(modules_to_install):
                _logger.warning(
                    "Not all instance modules were installed: "
                    f"{modules_to_install} -> {modules.mapped('name')}"
                )
            modules.button_immediate_install()
