Migration Sale
==============================

Migration helper for the module sale.

The version 9 add several field on the sale.order/sale.order.line
This module try to reduce the migration speed by pre-computing some field
before the migration so the migration duration will be improve.

A cron is configured to compute this field when sale order are done.

Fields added by the version 9 and precomputed
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sale.order.line
-----------------

price_total
price_reduce
price_tax
price_subtotal
currency_id
delivery_price (set to 0)

Note during the migration the field delivery_price is set to 0
for all order that are not in the draft state
In version 12 this field is not anymore a computed field and default value is 0
So this module just set 0 to this field

Field that are not yet supported by this module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

sale.order.line
----------------
qty_to_invoice
qty_invoiced
invoice_status

sale.order
-----------
invoice_status
