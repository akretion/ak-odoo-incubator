# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import secrets
from datetime import UTC, datetime, timedelta

import jwt

from odoo import Command, api, fields, models
from odoo.exceptions import AccessDenied


class ResUsers(models.Model):
    _inherit = "res.users"

    instance_db_jwt_secret_key = fields.Char()

    def _get_master_user_instance_default_groups(self):
        return self.env.ref("base.group_system")

    @api.model
    def _get_instance_user_from_master(self, master_user):
        return self.search([("login", "=", master_user.login)])

    @api.model
    def _create_instance_user_from_master(self, master_user):
        return self.create(
            {
                "login": master_user.login,
                "name": master_user.name,
                "groups_id": [
                    Command.set(self._get_master_user_instance_default_groups().ids)
                ],
            }
        )

    @api.model
    def _get_or_create_instance_user_from_master(self, master_user):
        if self.env.company.block_master_connection:
            raise AccessDenied(self.env._("Connection to master instance is blocked."))
        user = self._get_instance_user_from_master(master_user)
        if user:
            return user
        return self._create_instance_user_from_master(master_user)

    def _get_instance_db_jwt_token(self):
        if self.env.company.block_master_connection:
            raise AccessDenied(self.env._("Connection to master instance is blocked."))
        self.instance_db_jwt_secret_key = secrets.token_urlsafe(256)
        token = jwt.encode(
            {
                "exp": datetime.now(tz=UTC) + timedelta(minutes=2),
                "aud": self.login,
                "id": self.id,
            },
            self.instance_db_jwt_secret_key,
            algorithm="HS256",
        )
        return token

    def _check_instance_db_token(self, token):
        if self.env.company.block_master_connection:
            raise AccessDenied(self.env._("Connection to master instance is blocked."))
        try:
            jwt.decode(
                token,
                self.instance_db_jwt_secret_key,
                audience=self.login,
                options={"require": ["exp", "aud", "id"]},
                algorithms=["HS256"],
            )
            # Make it one-time:
            self.instance_db_jwt_secret_key = None
        except jwt.PyJWTError as e:
            raise AccessDenied(self.env._("Invalid Token")) from e
