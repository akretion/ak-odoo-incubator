# coding: utf-8
# © 2018
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import fields
from odoo.tests.common import TransactionCase

logger = logging.getLogger(__name__)


class TestSchedule(TransactionCase):
    def setUp(self):
        super(TestSchedule, self).setUp()
        self.res = self.env["resource.calendar"].search([], limit=1)

    def test__get_date(self):
        # 02/2/18: Friday, last day of the week
        cases = [
            {"sd": "2018-02-02 12:32:00", "delay": 1, "result": "2018-02-05"},
            {"sd": "2018-02-02 12:32:00", "delay": 2, "result": "2018-02-06"},
            {"sd": "2018-02-02 17:32:00", "delay": 1, "result": "2018-02-05"},
            {"sd": "2018-02-02 23:18:00", "delay": 1, "result": "2018-02-05"},
            {"sd": "2018-02-02 02:02:00", "delay": 1, "result": "2018-02-05"},
            {"sd": "2018-02-01 02:02:00", "delay": 1, "result": "2018-02-02"},
            {"sd": "2018-02-01 12:32:00", "delay": 1, "result": "2018-02-02"},
            {"sd": "2018-02-01 23:00:00", "delay": 1, "result": "2018-02-02"},
            {"sd": "2018-02-01 20:00:00", "delay": 2, "result": "2018-02-05"},
            {"sd": "2018-02-01 16:32:00", "delay": 9, "result": "2018-02-14"},
        ]
        for case in cases:
            sd = fields.Datetime.from_string(case["sd"])
            self.assertEqual(
                self.res.get_next_working_date(sd, case["delay"])
                .date()
                .isoformat(),
                case["result"],
                "{} + {}".format(case["sd"], case["delay"]),
            )

    def test_get_working_days(self):
        cases = [
            {"sd": "2018-02-01 12:32:00", "ed": "2018-02-01 14:32:00", "r": 1},
            {"sd": "2018-02-01 12:32:00", "ed": "2018-02-01 19:22:00", "r": 1},
            {"sd": "2018-02-01 12:32:00", "ed": "2018-02-02 12:32:00", "r": 2},
            {"sd": "2018-02-01 12:32:00", "ed": "2018-02-02 14:32:00", "r": 2},
            {"sd": "2018-02-01 12:32:00", "ed": "2018-02-02 19:22:00", "r": 2},
            {"sd": "2018-02-01 12:32:00", "ed": "2018-02-05 14:32:00", "r": 3},
            {"sd": "2018-02-01 09:14:00", "ed": "2018-02-06 19:44:00", "r": 4},
        ]
        for case in cases:
            sd = fields.Datetime.from_string(case["sd"])
            ed = fields.Datetime.from_string(case["ed"])
            self.assertEqual(
                self.res.get_working_days(sd, ed),
                case["r"],
                "{} - {}".format(case["ed"], case["sd"]),
            )
