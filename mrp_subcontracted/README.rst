.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

================================
Subcontracted Manfucatring Order
================================

This modules allows to bind a Bill of Materials to a service (product).

When a manufacturing order (MO) for this BOM is created, a purchase order (PO) for this service
will be created and linked to the MO.

This is useful in case of subcontracted manufacturing:
 - you may or not provide raw materials to a supplier
 - the supplier process the manufacturing (service)

This module make use of procurements.


Installation
============

To install this module, you need to:

#. Install the module

Configuration
=============

To configure this module, you need to:

#. Configure the service products: 
    - Ensure the product type is "service",
    - Check the flag property_subcontracted_service
    - Add the subcontractor as a supplier of this product.

#. Configure rules (for each warehouse):
    - Configure the predifined "Subcontracting_service procurement' rule in Inventory / Configuration / Routes. Set propagate flag to false.

#. Configure the Bill Of Matterials (BOM):
    - On the bill set a service product

Usage
=====

When a MO is created, if a service is attached in the BOM, a purchase order will be created.
The availability of the MO is forced to 'waiting' until the purchase is not done.

#. Go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

* All purchase order lines should be service (no buy products) because of the picking type manufacture
* A line should have only one (procurement, MO) associated

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
