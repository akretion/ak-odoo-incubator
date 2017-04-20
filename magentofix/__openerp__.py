# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Magento Fix",
    "version": "7.0.0.0",
    "depends": ["magentoerpconnect"],
    "author": "Akretion",
    "description": """This module will fix wrong sync data""",
    "website": "http://www.akretion.com/",
    "category": "Connector",
    "demo_xml": [],
    "data": [
        'data/cron.xml',
        ],
    'license': 'AGPL-3',
    "auto_install": False,
    "installable": True,
}
