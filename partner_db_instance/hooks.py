# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(env):
    import re

    from odoo.exceptions import AccessDenied
    from odoo.tools import config

    if not config.get("partner_db_instance_master"):
        raise RuntimeError(env._("partner_db_instance_master not set in config"))
    if not config.get("partner_db_instance_password"):
        raise RuntimeError(env._("partner_db_instance_password not set in config"))

    db = config["partner_db_instance_master"]
    if env.cr.dbname != db:
        raise AccessDenied(
            env._("You are not allowed to install this module on this instance")
        )

    if not config.get("dbfilter"):
        raise RuntimeError(
            env._("dbfilter must be set in config for partner_db_instance to work")
        )

    dbfilter = config["dbfilter"]
    dbfilter_re = re.compile(dbfilter.replace("%h", ".+").replace("%d", ".+"))
    if not dbfilter_re.match(env.cr.dbname):
        raise RuntimeError(
            env._("dbfilter should match the partner_db_instance_master database name")
        )
