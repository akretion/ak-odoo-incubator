.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License AGPL-3

=============
Pricelist Tax
=============


In Odoo the tax included or excluded is define on the tax level.
As the product is linked to the tax all pricelist for the product must be
tax included or tax excluded. You can not have a mix of solution with for exemple
- a public pricelist with base price tax included
- a professionnal pricelist with a base price tax ecluded

This case is a casual case for European company that have specific
pricelist for B2B with a base price tax excluded and a pricelist B2C tax included.

This module allow you to support this case.
You need to configure
- a taxed included on your product (this is required)
- create a fiscal position professional that map tax inc to tax exc
- create as much pricelist you want that includ or not the tax
