import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-akretion-ak-odoo-incubator",
    description="Meta package for akretion-ak-odoo-incubator Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-account_move_adyen_import>=16.0dev,<16.1dev',
        'odoo-addon-account_move_dalenys_import>=16.0dev,<16.1dev',
        'odoo-addon-account_refund_no_business_field>=16.0dev,<16.1dev',
        'odoo-addon-auth_oauth_redirect_fix>=16.0dev,<16.1dev',
        'odoo-addon-base_custom_export>=16.0dev,<16.1dev',
        'odoo-addon-fs_product>=16.0dev,<16.1dev',
        'odoo-addon-module_analysis_price>=16.0dev,<16.1dev',
        'odoo-addon-mrp_raw_material_from_config>=16.0dev,<16.1dev',
        'odoo-addon-product_dimension_net>=16.0dev,<16.1dev',
        'odoo-addon-project_estimate_step>=16.0dev,<16.1dev',
        'odoo-addon-project_time_in_day>=16.0dev,<16.1dev',
        'odoo-addon-proxy_action>=16.0dev,<16.1dev',
        'odoo-addon-purchase_edi_file>=16.0dev,<16.1dev',
        'odoo-addon-sale_delivery_no_invoice_free_shipping>=16.0dev,<16.1dev',
        'odoo-addon-sale_lot_config>=16.0dev,<16.1dev',
        'odoo-addon-zip_product_image>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
