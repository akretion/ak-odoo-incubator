{
    "name": "Block Confirm Flow",
    "summary": """Module to prevent validation of:
                    sale.order,
                    purchase.order,
                    mrp.production,
                    account.move""",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Uncategorized",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": " Akretion",
    "license": "AGPL-3",
    "application": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": ["sale", "purchase", "mrp", "account"],
    "data": [],
    "demo": [],
}
