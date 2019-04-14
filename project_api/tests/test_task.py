# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.tests.common import TransactionComponentCase
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
import json
import base64
from os import path, getenv
import logging

_logger = logging.getLogger(__name__)

DATA_PATH = path.join(path.dirname(path.abspath(__file__)), "data.json")
LEARN = getenv("LEARN")


def get_data():
    with open(DATA_PATH, "r") as f:
        try:
            return json.loads(f.read())
        except Exception:
            if LEARN:
                return {}
            else:
                raise


DATA = get_data()


class TestTask(TransactionComponentCase):
    def setUp(self, *args, **kwargs):
        super(TestTask, self).setUp(*args, **kwargs)
        self.env.user.image = self._get_image("partner-support-image.png")
        self.project = self.env.ref("project_api.project_project_1")
        self.partner = self.env.ref("project_api.partner_customer_help_desk")
        self.partner.help_desk_project_id = self.project
        collection = _PseudoCollection("project.project", self.env)
        self.work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            partner=self.partner,
        )

    def _get_image(self, name):
        image_path = path.dirname(path.abspath(__file__))
        f = open(path.join(image_path, "static", name))
        return base64.b64encode(f.read())

    def _update_json_data(self, case, vals):
        data = get_data()
        data[case]["output"] = vals
        with open(DATA_PATH, "w") as f:
            f.write(json.dumps(data, indent=4, sort_keys=True))

    def _sanitize(self, case, data):
        if case == "test_read_support_author":
            data.pop("update_date")
        elif case == "test_message_format":
            for elem in data:
                elem["author_id"].pop("update_date")
                elem.pop("date")
                elem.pop("id")
                elem.pop("tracking_value_ids")
                elem["subtype_id"] = elem["subtype_id"][1]
        elif case == "test_read_group":
            for elem in data:
                elem.pop("__domain")

    def _check_output(self, case, result):
        # json store tuple as list
        # so we convert in json before doing the comparaison
        result = json.loads(json.dumps(result))
        self._sanitize(case, result)
        self._sanitize(case, DATA[case]["output"])
        self.assertEqual(DATA[case]["output"], result)

    def _prepare_input(self, case, data):
        if case == "test_message_format":
            task = self.env.ref("project_api.project_task_3")
            data["ids"] = task.message_ids.ids
        elif case == "test_read":
            data["ids"] = [
                self.env.ref("project_api.project_task_1").id,
                self.env.ref("project_api.project_task_2").id,
            ]

    def test_run_all(self):
        data = get_data()
        for case, vals in data.items():
            service_name = vals["service_name"]
            method = vals["method"]
            _logger.info("Run automatic test %s, %s" % (service_name, method))
            service = self.work.component(usage=service_name)
            self._prepare_input(case, vals["input"])
            result = service.dispatch(method, params=vals["input"])
            if LEARN:
                self._update_json_data(case, result)
            else:
                if case in ("test_create", "test_message_post", "test_write"):
                    self.assertIsInstance(result, int)
                    # check that a contact customer have been created
                    contact = self.env["res.partner"].search(
                        [
                            ("customer_uid", "!=", False),
                            ("parent_id", "=", self.partner.id),
                        ]
                    )
                    self.assertEqual(len(contact), 1)
                elif case == "test_write__assigne":
                    # check that two contact customer have been created
                    contact = self.env["res.partner"].search(
                        [
                            ("customer_uid", "!=", False),
                            ("parent_id", "=", self.partner.id),
                        ]
                    )
                    self.assertEqual(len(contact), 2)
                else:
                    self._check_output(case, result)
            self.env.cr.rollback()
