Multi Company Holding Invoicing
===============================

This module allows to automatically invoice from sale order the customer or the supplier of the holding in multi-company environnement.
On Agreement, you must enter 'Holding Company' if you want invoice the holding on sale order and check if you want automatic invoicing for holding's customer or holding's supplier.
In the Sales Order, if you select Agreement whose Holding Company is set then the sales order must be invoiced via the Holding Company.
On Sale Order, you have a new field that indicates the holding invoice state and his associated invoice if necessary.
For holding's supplier, we create a grouped invoice on Holding Company if it exists otherwise on invoicing partner.
For holding's customer, we create a grouped invoice on invoicing partner.

Credits
=======

Contributors
------------

* Chafique Delli (chafique.delli@akretion.com)
* Sébastien Beau (sebastien.beau@akretion.com)
* David Béal (david.beal@akretion.com)
