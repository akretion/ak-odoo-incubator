.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

======================
Purchase PO Sent State
======================
Add a state on purchase in order to record when the PO is sent to supplier.
The workflow is this way : 
Creation of the purchase order at state RFQ.
When you send the RFQ by email, state goes to RFQ sent.
When you send the final PO by email, state goes to PO sent.
When it is all confirmed with the supplier, you can confirm the purchase order


Installation
============

To install this module, you need to:

#. Install the module


Known issues / Roadmap
======================

* Carefull, as the states are overiden, it could have conflicts with other
modules which add or remove states on purchase order
* It has not been tested with double po validation.


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

* Florian Da Costa <florian.dacosta@akretion.com> (Akretion)

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
