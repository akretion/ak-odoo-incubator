# coding: utf-8
# © 2016 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Active Previous Actived Crons',
    'summary': 'Unactive crons on install, reactive previously '
               'active one on module uninstall.',
    'description': """
Use case:

Your ERP is in production, and you have an issue.
You should stop the automatical tasks to understand what is the real problem.


* Install this module: all tasks (crons) are now inactive
* Fix the issue
* Uninstall this module: all tasks previously active, and only them,
  are now active.


When the production is repaired, you may forget to active one or more crons.
Some of them may run important features.

With this module, you can't forget anymore.


        """,
    'version': '8.0.1.0.0',
    'author': 'Akretion',
    'maintainer': 'Akretion',
    'category': 'Tools',
    'depends': [
        'base',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
    ],
    'installable': True,
    'license': 'AGPL-3',
}
