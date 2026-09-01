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
    _description = "Partner Database Instance"
    _inherit = ("mail.thread", "mail.activity.mixin")
    _rec_name = "subdomain"
    _order = "state desc, partner_id"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("live", "Live"),
            ("archived", "Archived"),
        ],
        compute="_compute_state",
        store=True,
        tracking=True,
        default="draft",
        required=True,
    )
    partner_id = fields.Many2one("res.partner", required=True)
    subdomain = fields.Char(
        compute="_compute_subdomain",
        store=True,
        precompute=True,
        required=True,
        readonly=False,
        tracking=True,
    )
    url = fields.Char(
        compute="_compute_url",
        readonly=True,
    )

    _sql_constraints = (
        ("subdomain_unique", "UNIQUE(subdomain)", "Subdomain must be unique"),
        ("partner_unique", "UNIQUE(partner_id)", "Partner must be unique"),
        ("db_name_unique", "UNIQUE(db_name)", "DB name must be unique"),
    )

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
    def db_name(self):
        base = self.master_instance.split("_")[0]
        return f"{base}_{self.subdomain}"

    @property
    def archived_db_name(self):
        return f"_archived_{self.db_name}"

    @contextmanager
    def instance_env(self, update_module=False):
        registry = Registry.new(self.db_name, False, None, update_module=update_module)
        with closing(registry.cursor()) as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            try:
                yield env
            except Exception:
                cr.rollback()
                raise
            else:
                cr.commit()  # pylint: disable=invalid-commit

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

    def _install_modules(self):
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

        self._install_modules()

    def action_deploy(self):
        for record in self:
            record.message_post(
                body=self.env._("Deploying database %s", record.db_name)
            )
            record._setup_database()
        self._compute_state()

    def action_archive(self):
        for record in self:
            record.message_post(
                body=self.env._("Archiving database %s", record.db_name)
            )
            close_db(record.db_name)
            db_rename(record.db_name, record.archived_db_name)
        self._compute_state()

    def action_unarchive(self):
        for record in self:
            record.message_post(
                body=self.env._("Redeploying database %s", record.db_name)
            )
            db_rename(record.archived_db_name, record.db_name)
        self._compute_state()

    def action_delete(self):
        for record in self:
            record.message_post(body=self.env._("Deleted database %s", record.db_name))
            db_drop(record.archived_db_name)
        self._compute_state()

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

    def action_sync_state(self):
        self._compute_state()

    def action_sync_state_all(self):
        self.search([])._compute_state()

    def write(self, vals):
        state = self.state
        old_db_name = (
            (self.archived_db_name if state == "archived" else self.db_name)
            if state != "draft"
            else None
        )
        result = super().write(vals)
        new_db_name = self.archived_db_name if state == "archived" else self.db_name
        if old_db_name and new_db_name != old_db_name:
            self.message_post(
                body=self.env._(
                    "Renamed database from %s to %s", old_db_name, new_db_name
                )
            )
            close_db(old_db_name)
            db_rename(old_db_name, new_db_name)
            self._compute_state()

        return result

    def unlink(self):
        self._compute_state()
        db_name = (
            (self.archived_db_name if self.state == "archived" else self.db_name)
            if self.state != "draft"
            else None
        )

        res = super().unlink()
        # Close and drop the database if it exists
        if db_name:
            close_db(db_name)
            db_drop(db_name)
        return res
