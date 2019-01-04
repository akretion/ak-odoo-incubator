# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015-TODAY Akretion (http://www.akretion.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
