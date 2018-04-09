.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

========================
MRP Subcontract Location
========================

This modules aims to put the right location subcontracted manufacturing orders.
At Sale order Validation, we do not know yet which supplier will produce which products.
We only have this information when the subcontrated PO linked to a MO is validated.
At this moment, we put the location on the raw material MO and the destination location on the MO's finished product.

When MO are chained, to avoid adding steps with internal picking between MO, we make the chained MO take the raw material (source location) directly on the previous MO dest location.

When subcontracting MOs, we also need to purchase and send the raw material directly at the subcontractor manufactory.
This module display an address field on POs to indicate at which subcontractor we send the PO, the picking is created to the subcontractor location.

We create one global warehouse for all subcontractors and one sublocation by subcontractor to avoid having one warehouse by subcontractor, which could become very difficult to manage.


Configuration
=============

To configure this module, you need to:

#. Configure the new created warehouse (Change the name, code...)
#. Change the warehouse main location to view type (name of location is stock by default)
#. Add one sublocation for each subcontractor and fill these new location on each subcontractor information (Sale & Purchase tab)


Known issues / Roadmap
======================

* ...

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Florian da Costa <florian.dacosta@akretion.com> (Akretion)

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* Akretion


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
