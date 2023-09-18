# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import csv

from odoo import models


class AbstractScriptProcessor(models.AbstractModel):
    _name = "abstract.script.processor"
    _description = "Abstract Script Processor"

    def _process_line(self, line):
        raise NotImplementedError()

    def run(self, data):
        headers = set()
        output = []
        for line in csv.reader(data):
            output.append(self._process_line(line))
            headers |= set(output.keys())
        return self.write_output(headers, output)

    def write_output(self, headers, output):
        writer = csv.DictWriter(
            output,
            delimiter=",",
            quotechar='"',
            fieldnames=headers,
        )

        return data
