# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
import requests_mock
import json
from os import path, getenv

DATA_PATH = path.join(path.dirname(path.abspath(__file__)), 'data.json')
LEARN = getenv('LEARN')


def get_data():
    with open(DATA_PATH, 'r') as f:
        try:
            return json.loads(f.read())
        except Exception:
            if LEARN:
                return {}
            else:
                raise


DATA = get_data()


class TestTask(TransactionCase):

    def _get_method(self):
        return self._testMethodName.split('__')[0].replace('test_', '')

    def _get_task_ids(self, refs):
        ids = []
        for xmlid in refs:
            _, res_id = self.env['ir.model.data'].xmlid_to_res_model_res_id(
                xmlid, raise_if_not_found=True)
            ids.append(res_id)
        return ids

    def _update_json_data(self, vals):
        data = get_data()
        case = self._testMethodName
        method = self._get_method()
        if case not in data:
            data[case] = {}
        data[case].update({
            'input': vals,
            'method': method,
            'service_name': 'task',
            })
        with open(DATA_PATH, 'w') as f:
            f.write(json.dumps(data, indent=4, sort_keys=True))

    def _activate_mock(self, m, case=None, method=None):
        case = case or self._testMethodName
        method = method or self._get_method()
        url = 'http://localhost:8069/project-api/task/%s' % (method)
        if LEARN:
            result = {}  # we do not care
        else:
            result = DATA[case]['output']
        m.post(url, json=result)

    def _check_input(self, request_input):
        self.assertEqual(DATA[self._testMethodName]['input'], request_input)

    def test_read_group(self):
        with requests_mock.Mocker() as m:
            self._activate_mock(m)
            res = self.env['external.task'].read_group(
                groupby=["stage_name"],
                fields=["stage_name", "name"],
                domain=[],
                offset=0,
                lazy=True,
                limit=False,
                orderby=False,
                )
            request_input = m.request_history[0].json()
            if LEARN:
                self._update_json_data(request_input)
            else:
                self._check_input(request_input)
                self.assertEqual(len(res), 3, 'we expect 3 columns')
                stages = [x['stage_name'] for x in res]
                self.assertEqual(stages, ['To Do', 'In Progress', 'Done'])

    def test_search(self):
        with requests_mock.Mocker() as m:
            self._activate_mock(m)
            res = self.env['external.task'].search(
                domain=[["stage_name", "=", "To Do"]],
                )
            request_input = m.request_history[0].json()
            if LEARN:
                self._update_json_data(request_input)
            else:
                self._check_input(request_input)
                self.assertEqual(len(res), 1, 'we expect 1 task')
                self.assertIsInstance(res[0], type(self.env['external.task']))

    def test_search__count(self):
        with requests_mock.Mocker() as m:
            self._activate_mock(m)
            res = self.env['external.task'].search(
                domain=[["stage_name", "=", "To Do"]],
                count=True,
                )
            request_input = m.request_history[0].json()
            if LEARN:
                self._update_json_data(request_input)
            else:
                self._check_input(request_input)
                self.assertEqual(res, 1)

    def test_read(self):
        with requests_mock.Mocker() as m:
            self._activate_mock(m)
            if LEARN:
                task_ids = self._get_task_ids([
                    'project_api.project_task_1',
                    'project_api.project_task_2',
                    ])
            else:
                task_ids = DATA[self._testMethodName]['input']['ids']
            res = self.env['external.task'].browse(task_ids).read(fields=[
                "stage_name",
                "name",
                ])
            request_input = m.request_history[0].json()
            if LEARN:
                self._update_json_data(request_input)
            else:
                self._check_input(request_input)
                self.assertEqual(len(res), 2)
                names = [x['name'] for x in res]
                self.assertEqual(names, [
                    u'Bug when sending email',
                    u'Need to add a new columns in report A'])

    def test_create(self):
        with requests_mock.Mocker() as m:
            self._activate_mock(m)
            res = self.env['external.task'].create({
                'name': 'Test',
                'description': 'Creation test',
                })
            request_input = m.request_history[0].json()
            if LEARN:
                self._update_json_data(request_input)
            else:
                self._check_input(request_input)
                self.assertEqual(len(res), 1)
                self.assertIsInstance(res, type(self.env['external.task']))

    def test_write(self):
        with requests_mock.Mocker() as m:
            self._activate_mock(m)
            if LEARN:
                task_ids = self._get_task_ids([
                    'project_api.project_task_1',
                    'project_api.project_task_2',
                    ])
            else:
                task_ids = DATA[self._testMethodName]['input']['ids']
            res = self.env['external.task'].browse(task_ids).write({
                'description': 'Duplicated task of issue #112',
                })
            request_input = m.request_history[0].json()
            if LEARN:
                self._update_json_data(request_input)
            else:
                self._check_input(request_input)
                self.assertEqual(res, True)

    def test_read_support_author(self):
        with requests_mock.Mocker() as m:
            self._activate_mock(m)
            if LEARN:
                uid = self.env.user.partner_id.id
            else:
                uid = DATA['test_read_support_author']['input']['uid']
            res = self.env['external.task']._call_odoo(
                'read_support_author', {'uid': uid})
            request_input = m.request_history[0].json()
            if LEARN:
                self._update_json_data(request_input)
            else:
                self._check_input(request_input)
                self.assertEqual(res['uid'], uid)
                self.assertIn('name', res)
                self.assertIn('image', res)
                self.assertIn('update_date', res)

    def test_message_format(self):
        with requests_mock.Mocker() as m:
            support_team = self.env.ref('project_api_client.support_team')
            # Ensure that there is not partner in the team
            support_team.child_ids.unlink()
            self._activate_mock(m)
            self._activate_mock(
                m, 'test_read_support_author', 'read_support_author')
            if LEARN:
                task_id = self._get_task_ids(['project_api.project_task_3'])[0]
                messages = self.env['mail.message'].search([
                    ('res_id', '=', task_id),
                    ('model', '=', 'project.task'),
                    ])
                mids = messages.ids
            else:
                mids = DATA['test_message_format']['input']['ids']
            mids = ['external/%s' % mid for mid in mids]
            res = self.env['mail.message'].browse(mids).message_format()
            request_input = m.request_history[0].json()
            if LEARN:
                self._update_json_data(request_input)
            else:
                self._check_input(request_input)
                self.assertEqual(len(res), 1)
                # Check that support partner have been created
                self.assertEqual(len(support_team.child_ids), 1)

    def test_message_post(self):
        with requests_mock.Mocker() as m:
            if LEARN:
                task_id = self._get_task_ids(['project_api.project_task_6'])[0]
            else:
                task_id = DATA['test_message_post']['input']['_id']
            self._activate_mock(m)
            res = self.env['external.task'].browse(task_id).message_post(
                body="my comment")
            request_input = m.request_history[0].json()
            if LEARN:
                self._update_json_data(request_input)
            else:
                self._check_input(request_input)
                self.assertIn('external/', res)
