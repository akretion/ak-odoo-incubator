# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Multicompany submittal workflows",
    "summary": "Base building block for multicompany submittal workflows",
    "license": "AGPL-3",
    "version": "12.0.1.0.0",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainer": "Akretion",
    "category": "Sales",
    "depends": ["base", "base_multicompany_submit", "sale_management"],
    "data": [
        "security/groups.xml",
        "data/ir_rule.xml",
        "views/product_approval.xml",
        "security/ir.model.access.csv",
    ],
    "maintainers": ["kevinkhao", "sebastienbeau"],
    "website": "http://www.akretion.com/",
    "installable": True,
}
