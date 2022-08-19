Put this code in your custom module according to model
you want forbid creation.

.. code:: python

    class AccountMove(models.Model):
        _inherit = ["account.move", "forbidden.model"]
        _name = "account.move"


    class SaleOrder(models.Model):
        _inherit = ["sale.order", "forbidden.model"]
        _name = "sale.order"


    class PurchaseOrder(models.Model):
        _inherit = ["purchase.order", "forbidden.model"]
        _name = "purchase.order"
