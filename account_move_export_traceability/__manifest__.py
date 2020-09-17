# © 2019 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Accounting Move Export Traceability",
    "version": "12.0.0.1.0.1",
    "author": "Akretion",
    "category": "account",
    "depends": [
        "account_export_csv",
        "attachment_synchronize",
    ],
    "website": "https://www.akretion.com",
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/move_export_view.xml",
        "views/settings_view.xml",
        "data/task.xml",
        "data/cron.xml",
        "wizards/account_csv_export_view.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
