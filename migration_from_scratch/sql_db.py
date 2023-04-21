# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import os

from odoo import tools
from odoo.sql_db import Connection, ConnectionPool, _Pool  # noqa


def connection_info_for_external_database():
    db_name = os.environ.get("EXTERNAL_DB_NAME")
    connection_info = {"database": db_name}
    for p in ("HOST", "PORT", "USER", "PASSWORD"):
        cfg = os.environ.get("EXTERNAL_DB_" + p)
        if cfg:
            connection_info[p.lower()] = cfg
    return db_name, connection_info


def get_external_cursor():
    global _Pool
    if _Pool is None:
        _Pool = ConnectionPool(int(tools.config["db_maxconn"]))
    db, info = connection_info_for_external_database()
    return Connection(_Pool, db, info).cursor()
