import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-akretion-ak-odoo-incubator",
    description="Meta package for akretion-ak-odoo-incubator Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-account_move_export_traceability',
        'odoo12-addon-forbid_record_creation',
        'odoo12-addon-mail_via',
        'odoo12-addon-proxy_action',
        'odoo12-addon-proxy_action_trivial_example',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
