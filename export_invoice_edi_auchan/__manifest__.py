{
    "name": "Custom export invoice edi format Auchan",
    "version": "16.0.0.0.0",
    "author": "Akretion",
    "category": "EDI",
    "website": "https://akretion.com",
    "license": "AGPL-3",
    "depends": [
        "account",
        "stock_picking_invoice_link",
        "fs_storage",
        "attachment_synchronize_record",
    ],
    "data": [
        "data/task_data.xml",
        "views/res_partner.xml",
        "views/account_move.xml",
    ],
}
