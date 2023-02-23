# Copyright 2023 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.tests import SavepointCase


class TestDefaultChannel(SavepointCase):
    def test_default_channel(self):
        self.env["res.partner"].search([], limit=1).with_delay().write({"name": "Foo"})
        job = self.env["queue.job"].search(
            [("func_string", "ilike", "write({'name': 'Foo'})")]
        )
        self.assertEqual(job.channel, "root.default.basic_job")
