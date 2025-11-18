import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-akretion-ak-odoo-incubator",
    description="Meta package for akretion-ak-odoo-incubator Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-account_move_line_mass_edit_account',
        'odoo14-addon-attachment_asset_in_db',
        'odoo14-addon-base_custom_export',
        'odoo14-addon-dash_shared',
        'odoo14-addon-database_age_cron',
        'odoo14-addon-forbid_record_creation',
        'odoo14-addon-intercompany_shared_contact',
        'odoo14-addon-label_wizard',
        'odoo14-addon-mail_env_whitelist',
        'odoo14-addon-mail_preview_send',
        'odoo14-addon-mail_unique_layout',
        'odoo14-addon-module_analysis_price',
        'odoo14-addon-product_pricelist_per_attribute_value',
        'odoo14-addon-product_supplierinfo_group_per_attribute_value',
        'odoo14-addon-product_supplierinfo_per_attribute_value',
        'odoo14-addon-product_supplierinfo_per_attribute_value_intercompany',
        'odoo14-addon-product_uom_force_change',
        'odoo14-addon-project_estimate_step',
        'odoo14-addon-project_time_in_day',
        'odoo14-addon-proxy_action',
        'odoo14-addon-purchase_edi_file',
        'odoo14-addon-purchase_lot',
        'odoo14-addon-queue_job_cancel_dead_job',
        'odoo14-addon-queue_job_default_channel',
        'odoo14-addon-secondary_analytic_account',
        'odoo14-addon-security_rule_not_editable',
        'odoo14-addon-stock_inventory_simple_valuation',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
