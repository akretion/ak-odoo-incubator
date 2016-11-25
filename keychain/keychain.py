# -*- coding: utf-8 -*-
# © 2016 Akretion Mourad EL HADJ MIMOUNE, David BEAL, Raphaël REVERDY
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from functools import wraps

from openerp import models, fields, api
from openerp.exceptions import ValidationError
import openerp.tools.config as config

from cryptography.fernet import Fernet
import logging
import json

_logger = logging.getLogger(__name__)


def implemented_by_keychain(func):
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        fun_name = func.__name__
        fun = '_%s%s' % (cls.namespace, fun_name)
        if not hasattr(cls, fun):
            fun = '_default%s' % (fun_name)
        return getattr(cls, fun)(*args, **kwargs)
    return wrapper


class AccountModel(models.Model):
    _name = 'keychain.account'

    name = fields.Char(required=True, help="Humain readable label")
    technical_name = fields.Char(
        required=True,
        help="Technical name. Must be unique")

    namespace = fields.Selection([], help="Type of account", required=True)

    login = fields.Char(help="Login")
    clear_password = fields.Char(
        help="Password. Leave empty if no changes",
        inverse='_set_password',
        store=False)
    password = fields.Char(
        name="Encrypted password",
        help="Password is derived from clear_password",
        readonly=True)

    data = fields.Text(help="Additionnal data as json")

    def get_password(self):
        return self._decode_password(self.password)

    def _get_data(self):
        return self._parse_data(self.data)

    @api.constrains('data')
    def _check_data(self):
        """Ensure valid input in data field."""
        for account in self:
            if account.data:
                parsed = account._parse_data(account.data)
                if not account._validate_data(parsed):
                    raise ValidationError("Data not valid")

    def _set_password(self):
        for rec in self:
            rec.password = rec._encode_password(rec.clear_password)

    @api.multi
    def write(self, vals):
        """At this time there is no namespace set."""
        if not vals.get('data') and not self.data:
            vals['data'] = self._serialize_data(self._init_data())
        return super(AccountModel, self).write(vals)

    @implemented_by_keychain
    def _validate_data(self, data):
        pass

    @implemented_by_keychain
    def _init_data(self):
        pass

    @staticmethod
    def _serialize_data(data):
        return json.dumps(data)

    @staticmethod
    def _parse_data(data):
        try:
            return json.loads(data)
        except ValueError:
            raise ValidationError("Data not valid JSON")

    @classmethod
    def _encode_password(cls, data):
        cipher = cls._get_cipher()
        return cipher.encrypt(str(data))

    @classmethod
    def _decode_password(cls, data):
        cipher = cls._get_cipher()
        return cipher.decrypt(str(data))

    @staticmethod
    def _get_cipher():
        key = config['keychain_key']
        return Fernet(key)
