# Copyright 2026 Akretion (http://www.akretion.com).
# @author Florian Mounier <florian.mounier@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import sys

from odoo import models


class Kalong(models.AbstractModel):
    _name = "kalong"
    _description = "Kalong"

    def shell(self):
        # Launch a shell with special globals
        from kalong.communication import communicate

        frame = sys._getframe()
        frame.f_globals["kalong"] = self
        frame.f_globals["env"] = self.env
        communicate(frame, "shell", [])
