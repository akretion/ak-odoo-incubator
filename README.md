
<!-- /!\ Non OCA Context : Set here the badge of your runbot / runboat instance. -->
[![Pre-commit Status](https://github.com/akretion/ak-odoo-incubator/actions/workflows/pre-commit.yml/badge.svg?branch=18.0)](https://github.com/akretion/ak-odoo-incubator/actions/workflows/pre-commit.yml?query=branch%3A18.0)
[![Build Status](https://github.com/akretion/ak-odoo-incubator/actions/workflows/test.yml/badge.svg?branch=18.0)](https://github.com/akretion/ak-odoo-incubator/actions/workflows/test.yml?query=branch%3A18.0)
[![codecov](https://codecov.io/gh/akretion/ak-odoo-incubator/branch/18.0/graph/badge.svg)](https://codecov.io/gh/akretion/ak-odoo-incubator)
<!-- /!\ Non OCA Context : Set here the badge of your translation instance. -->

<!-- /!\ do not modify above this line -->

# Akretion Odoo Module Incubator

Misc Odoo modules maturing before going to a specific repo

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[account_invoice_no_proforma](account_invoice_no_proforma/) | 18.0.1.0.0 |  | Avoid proforma invoice PDF when invoice is posted. If the pdf is not attached to the invoice because pdf was not properly sent by Odoo, then when you print the pdf, it is a PROFORMA invoice. This modules aims to avoid this proforma mention.
[gitlab_integration](gitlab_integration/) | 18.0.1.0.0 | <a href='https://github.com/paradoxxxzero'><img src='https://github.com/paradoxxxzero.png' width='32' height='32' style='border-radius:50%;' alt='paradoxxxzero'/></a> | Integration with Gitlab for project management
[project_estimate_step](project_estimate_step/) | 18.0.1.0.0 |  | Add step estimation for project
[project_task_urgency](project_task_urgency/) | 18.0.1.0.0 | <a href='https://github.com/paradoxxxzero'><img src='https://github.com/paradoxxxzero.png' width='32' height='32' style='border-radius:50%;' alt='paradoxxxzero'/></a> | Add urgency to project tasks
[project_time_in_day](project_time_in_day/) | 18.0.1.0.0 |  | Compute time in days

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Akretion
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
<!-- /!\ Non OCA Context : Set here the full description of your organization. -->
