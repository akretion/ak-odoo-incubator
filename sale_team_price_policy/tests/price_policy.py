# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp.tests.common import TransactionCase

logger = logging.getLogger(__name__)


class TestPricePolicy(TransactionCase):

    def setUp(self):
        super(TestPricePolicy, self).setUp()

    def test_sales(self):
        ''
