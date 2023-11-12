# coding: utf-8
# © 2016 David BEAL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Module report',
    'summary': "Report on modules: authors charts, etc.",
    'version': '8.0.0.0.1',
    'category': 'base',
    'author': 'Akretion',
    'description': """
Report on modules: authors charts, etc.

Roadmap:
- % modules abrité par OCA
- filtrage facile pour only installed modules
- nombre et % de modules non partagé: déclaration d'un chemin dans ir.config.parameter
- nombre de lignes de code python total / nbr de lignes sous OCA
- nombre de modules sans test unitaire
- date de dernière mise à jour du code source / module

Author: David BEAL
""",
    'depends': [
        'base',
    ],
    'website': 'http://www.akretion.com/',
    'data': [
        'report/module.xml',
    ],
    'installable': True,
    'license': 'AGPL-3',
}
