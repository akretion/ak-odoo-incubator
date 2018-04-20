Multi Company Holding Invoicing
===============================

This module allows to automatically invoice from delivery order the customer or the supplier of the holding in multi-company environnement.
On Agreement, you must enter 'Holding Company' if you want invoice the holding on picking and check if you want automatic invoicing for holding's customer or holding's supplier.
On Sale Order, if you select Agreement whose Holding Company is set then we invoice compulsorily on delivery order.
On Delivery Order, you have a new field that indicates the holding invoice state and his associated invoice if necessary.
For holding's supplier, we create a grouped invoice on Holding Company if it exists otherwise on invoicing partner.
For holding's customer, we create a grouped invoice on invoicing partner.

Credits
=======

Contributors
------------

* Chafique Delli (chafique.delli@akretion.com)
* Sébastien Beau (sebastien.beau@akretion.com)
* David Béal (david.beal@akretion.com)

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.
