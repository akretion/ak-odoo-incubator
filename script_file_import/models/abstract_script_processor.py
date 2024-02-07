# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import csv
import io
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AbstractScriptProcessor(models.AbstractModel):
    _name = "abstract.script.processor"
    _description = "Abstract Script Processor"

    def _process_line(self, line):
        raise NotImplementedError()

    def run(self, data):
        headers = set()
        output = []
        in_file = io.StringIO(base64.b64decode(data).decode("utf-8"))
        reader = csv.DictReader(in_file)
        for idx, line in enumerate(reader):
            _logger.info("Process line %s", idx)
            self.flush()
            try:
                with self.env.cr.savepoint():
                    self._process_line(line)
            except Exception as e:
                line["error"] = str(e)
                output.append(line)
                _logger.error("Script import error %s", e)
        headers = ["error"] + reader.fieldnames
        return self.write_output(headers, output, reader.dialect)

    def write_output(self, headers, data, dialect):
        f = io.StringIO()
        writer = csv.DictWriter(
            f,
            dialect=dialect,
            fieldnames=headers,
        )
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        f.seek(0)
        return base64.b64encode(f.read().encode("utf-8"))
