# © 2022 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class Test(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
