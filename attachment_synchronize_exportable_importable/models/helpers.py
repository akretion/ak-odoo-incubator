# Copyright 2023 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import csv
from io import StringIO


def format_export_to_csv(data: list):
    csv_file = StringIO()
    writer = csv.DictWriter(csv_file, fieldnames=data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    csv_file.seek(0)
    return csv_file
