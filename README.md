
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/akretion/ak-odoo-incubator/actions/workflows/pre-commit.yml/badge.svg?branch=14.0)](https://github.com/akretion/ak-odoo-incubator/actions/workflows/pre-commit.yml?query=branch%3A14.0)
[![Build Status](https://github.com/akretion/ak-odoo-incubator/actions/workflows/test.yml/badge.svg?branch=14.0)](https://github.com/akretion/ak-odoo-incubator/actions/workflows/test.yml?query=branch%3A14.0)
[![codecov](https://codecov.io/gh/akretion/ak-odoo-incubator/branch/14.0/graph/badge.svg)](https://codecov.io/gh/akretion/ak-odoo-incubator)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# Generic Odoo module in incubation

The modules present in this repo should go to OCA on the long run, they are still not used a lot and still need to prove themselves

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_move_line_mass_edit_account](account_move_line_mass_edit_account/) | 14.0.1.0.0 |  | Give the possibility to edit in mass the account on move line
[attachment_asset_in_db](attachment_asset_in_db/) | 14.0.1.0.0 |  | Always store odoo asset in database
[base_custom_export](base_custom_export/) | 14.0.1.0.0 |  | Base Customer Export
[dash_shared](dash_shared/) | 14.0.1.0.0 | [![Kev-Roche](https://github.com/Kev-Roche.png?size=30px)](https://github.com/Kev-Roche) | SUMMARY
[database_age_cron](database_age_cron/) | 14.0.1.0.0 |  | Run a cron that determines database age
[forbid_record_creation](forbid_record_creation/) | 14.0.2.0.0 |  | Avoid to create test data in sale, purchase, etc.
[intercompany_shared_contact](intercompany_shared_contact/) | 14.0.1.0.0 |  | User of each company are contact of a company partner. All child address of a company are automatically shared
[label_wizard](label_wizard/) | 14.0.1.0.0 |  | Wizard for choosing how many labels to print
[mail_unique_layout](mail_unique_layout/) | 14.0.1.0.0 |  | Use unique layout for most common emails
[module_analysis_price](module_analysis_price/) | 14.0.1.0.0 |  | Module Analysis Price
[product_pricelist_per_attribute_value](product_pricelist_per_attribute_value/) | 14.0.1.0.0 |  | Allows to have pricelist rule by product attribute value.
[product_uom_force_change](product_uom_force_change/) | 14.0.1.0.0 |  | Allow to force a uom change an already used product
[project_estimate_step](project_estimate_step/) | 14.0.1.0.0 |  | Add step estimation for project
[project_time_in_day](project_time_in_day/) | 14.0.1.0.0 |  | Compute time in days
[proxy_action](proxy_action/) | 14.0.1.0.1 |  | Proxy Action
[purchase_edi_file](purchase_edi_file/) | 14.0.1.0.0 |  | Purchase EDI file
[purchase_lot](purchase_lot/) | 14.0.1.0.0 |  | Purchase Lot
[queue_job_cancel_dead_job](queue_job_cancel_dead_job/) | 14.0.1.0.0 |  | Cancel dead pending job
[queue_job_default_channel](queue_job_default_channel/) | 14.0.1.0.0 |  | Default channel for queue job
[security_rule_not_editable](security_rule_not_editable/) | 14.0.1.0.0 |  | Forbid editing rule form UI force using code
[stock_inventory_simple_valuation](stock_inventory_simple_valuation/) | 14.0.1.0.0 | [![bealdav](https://github.com/bealdav.png?size=30px)](https://github.com/bealdav) [![PierrickBrun](https://github.com/PierrickBrun.png?size=30px)](https://github.com/PierrickBrun) [![mourad-ehm](https://github.com/mourad-ehm.png?size=30px)](https://github.com/mourad-ehm) [![kevinkhao](https://github.com/kevinkhao.png?size=30px)](https://github.com/kevinkhao) | Valuation of inventories according to custom rules

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Akretion
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->
