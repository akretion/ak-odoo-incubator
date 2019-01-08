Put this code in your custom module according to model
you want forbid creation.

.. code:: python

    class AccountInvoice(models.Model):
        _inherit = ['account.invoice', 'forbidden.model']
        _name = 'account.invoice'


    class PosOrder(models.Model):
        _inherit = ['pos.order', 'forbidden.model']
        _name = 'pos.order'
