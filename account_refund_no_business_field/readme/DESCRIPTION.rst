When creating a refund with a different mode than 'modify' (Full refund and new draft invoice), avoid copying business fields (which are the link between invoice lines and sale or purchase lines in native Odoo).
These business fields impact the quantity invoiced on sale and purchase order lines, decreasing it.

The main case this modules aims to fix is the following :
A sale order is fully invoiced. A refund is made on this invoice, the quantity invoiced is decreased and the invoicing state of the sale order goes back to "to invoice".
Then, a second invoice may be generated.
This is especially an issue when using sale_automatic_workflow with automatic invoice creation.
