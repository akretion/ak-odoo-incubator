# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Project API client',
    'summary': 'Module add a new entry to follow'
               'your project in the integrator ERP',
    "version": "8.0.1.0.0",
    "category": "Project Management",
    'author': "Akretion",
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'keychain',
        'base_suspend_security',
        'mail',
    ],
    'data': [
        'views/project_view.xml',
        'demo/keychain_demo.xml',
        'data/partner_data.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
