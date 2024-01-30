# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Multi Download',
    'description': """
        Wizard to download selected invoices""",
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Akretion',
    'website': 'akretion.com',
    'depends': [
        "account",
    ],
    'data': [
        "wizards/invoice_download.xml",
        "security/ir.model.access.csv",
    ],
    'demo': [
    ],
}
