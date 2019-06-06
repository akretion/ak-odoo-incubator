.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

========================
MRP Subcontract Location
========================

This modules aims to put the right location for subcontracted Manufacturing Orders (MO).
At Sale Order (SO) validation, we do not know yet which subcontractors will be choosen.
We only have this information when the subcontrated PO linked to a MO is validated.
At this moment, we put the location on the raw materials and on the destination location of the finished product.

When MOs are chained, to avoid adding steps with internal picking between MO, we make the chained MO take the raw material (source location) directly from the previous MO dest location.

When subcontracting MOs, we also need to purchase and send the raw material directly at the subcontractor manufactory.
This module display an address field on POs to indicate at which subcontractor we send the PO, the picking is created to the subcontractor location.

A cron will create the inter warehouses routes automatically and set the right roots on products. (like Supplier2: Supply from Supplier 1)


Remarks:

- Use module stock_interwarehouse_delay if you want to manage transit delays.


Configuration
=============

To configure this module, you need to:

#. Create as many warehouses as needed (At least one per supplier whom does manufacturing). Set the partner of the warehouse to the supplier (it can be his plant facility).
#. Set the picking type id of the BOM to warehouse_of_the_supplier.manufacturing


Known issues / Roadmap
======================

* All lines should have the same destination

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
* Raphaël Reverdy <raphael.reverdy@akretion.com> (Akretion)

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
