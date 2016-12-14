# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.osv import orm
from datadog import statsd


class DatadogCollect(orm.TransientModel):
    _name = "datadog.collect"

    def _collect_data_on_job(self, cr, uid):
        cr.execute("""SELECT
            split_part(func_string, ',', 1) AS nbr,
            state,
            count(id)
        FROM queue_job
        WHERE state != 'done'
        GROUP BY state, split_part(func_string, ',', 1)""")
        res = {}
        total = 0
        for func_string, state, count in cr.fetchall():
            func_string_shorted = func_string.replace('(', '.')\
                .replace("'", '').replace('openerp.addons.', '')
            res["%s.%s" % (func_string_shorted, state)] = count
            total += count
        res['job.total'] = total
        return res

    def _send(self, method, data):
        for key in data:
            method(key, data[key])

    def _run(self, cr, uid):
        self._send(statsd.histogram, self._collect_data_on_job(cr, uid))
