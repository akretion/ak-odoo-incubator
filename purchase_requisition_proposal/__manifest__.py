# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Requirement Proposal",
    "summary": "SUMMARY",
    "version": "14.0.1.0.0",
    "category": "CAT",
    "website": "https://github.com/akretion/ak-odoo-incubator",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "purchase_requisition",
        "purchase_sale_inter_company",
        "mail",
    ],
    "data": [
        "data/data.xml",
        "views/purchase_order.xml",
        "views/sale_order.xml",
        "views/purchase_requisition.xml",
        "views/purchase_requisition_type.xml",
        "wizard/wizard_requisition_proposal.xml",
        "views/ir_config.xml",
        "security/ir.model.access.csv",
        "security/purchase_requisition_security.xml",
    ],
}
