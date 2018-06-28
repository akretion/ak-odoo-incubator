.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========================
Purchase Order Line Extract
===========================

This module allow you to flag some purchase order as Open Orders. If an order is flaggued, it is not possible to receive the product from the picking.
Instead, you can create a new confirmed purchase order from one or more open order.

Usage
=====

Go to purchase order menu, select the concerned purchase orders and click "more actions", then "Extract purchase lines"

It is typically used if you have very big purchase orders with multipe incoming shipment. It allows you to have a purchase order with exactly what you will receive.

Known Issue
============

This feature is not available for a make to order process.
If any purchase order line is linked to a procurement with a move_dest_id, the feature won't be available.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Florian da Costa <florian.dacosta@akretion.com>

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

