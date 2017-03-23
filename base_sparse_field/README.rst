
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Base Sparse Fields
====================

This module backport the master module in order to have the
sparse field available with the new api

Be carefull the field "serialisation_field_id" is empty when adding a field
using the new api, this do not have impact on odoo framework but can have one
on your custom module.
