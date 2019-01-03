# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import TransactionComponentCase
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
import requests_mock
import json
from os import path, getenv
import logging
_logger = logging.getLogger(__name__)

DATA_PATH = path.join(path.dirname(path.abspath(__file__)), 'data.json')
LEARN = getenv('LEARN')

def get_data():
    with open(DATA_PATH, 'r') as f:
        try:
            return json.loads(f.read())
        except:
            if LEARN:
                return {}
            else:
                raise

DATA = get_data()


class TestTask(TransactionComponentCase):

    def setUp(self, *args, **kwargs):
        super(TestTask, self).setUp(*args, **kwargs)
        self.project = self.env.ref('project_api.project_project_1')
        collection = _PseudoCollection('project.project',  self.env)
        self.work = WorkContext(
            model_name='rest.service.registration',
            collection=collection,
            project=self.project)

    def _update_json_data(self, case, vals):
        data = get_data()
        data[case]['output'] = vals
        with open(DATA_PATH, 'w') as f:
            f.write(json.dumps(data, indent=4, sort_keys=True))

    def _check_output(self, case, result):
        # json store tuple as list
        # so we convert in json before doing the comparaison
        result = json.loads(json.dumps(result))
        self.assertEqual(DATA[case]['output'], result)

    def test_run_all(self):
        data = get_data()
        for case, vals in data.items():
            service_name = vals['service_name']
            method = vals['method']
            _logger.info(
                'Run automatic test %s, %s' % (service_name, method))
            service = self.work.component(usage=service_name)
            result = service.dispatch(method, params=vals['input'])
            if LEARN:
                self._update_json_data(case, result)
            else:
                if case == 'test_create':
                    self.assertIsInstance(result, int)
                else:
                    self._check_output(case, result)
            self.env.cr.rollback()
