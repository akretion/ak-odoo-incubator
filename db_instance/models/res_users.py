# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from odoo import fields, models
from odoo.exceptions import AccessDenied


class ResUsers(models.Model):
    _inherit = "res.users"

    instance_db_jwt_secret_key = fields.Char()

    def _get_instance_db_jwt_token(self):
        self.instance_db_jwt_secret_key = secrets.token_urlsafe(256)
        token = jwt.encode(
            {
                "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=2),
                "aud": self.login,
                "id": self.id,
            },
            self.instance_db_jwt_secret_key,
            algorithm="HS256",
        )
        return token

    def _check_instance_db_token(self, token):
        try:
            jwt.decode(
                token,
                self.instance_db_jwt_secret_key,
                audience=self.login,
                options={"require": ["exp", "aud", "id"]},
                algorithms=["HS256"],
            )
        except jwt.PyJWTError as e:
            raise AccessDenied(self.env._("Invalid Token")) from e
