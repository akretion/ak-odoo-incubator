# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp.osv import orm
from datadog import statsd
from collections import defaultdict


class DatadogCollect(orm.TransientModel):
    _name = "datadog.collect"

    def _collect_data_on_job(self, cr, uid):
        cr.execute("""SELECT
            model_name,
            state,
            count(id)
        FROM queue_job
        WHERE state != 'done'
        GROUP BY state, model_name""")
        res = {}
        total = defaultdict(int)
        for model, state, count in cr.fetchall():
            for prefix in ['magento.', 'prestashop.']:
                model = model.replace(prefix, '')
            statsd.histogram('job.%s' % state, count, tags=[model])
            total['total'] += count
            total['job.%s' % state] += count
        for key, value in total.items():
            statsd.histogram(key, value)
        return res

    def _run(self, cr, uid):
        self._collect_data_on_job(cr, uid)
