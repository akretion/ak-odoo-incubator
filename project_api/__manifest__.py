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
    'name': 'Project API',
    'summary': 'Expose a json-rpx like API on top of base_rest',
    "version": "10.0.1.0.0",
    "category": "Project Management",
    'author': "Akretion",
    'website': '',
    'license': 'AGPL-3',
    'depends': [
        'auth_api_key',
        'base_rest',
        'project',
    ],
    'data': [
        'views/project_view.xml',
        'demo/project_demo.xml',
    ],
    'installable': True,
    'application': True,
}
