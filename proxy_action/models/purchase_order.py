
from odoo import api, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_send_proxy_action_fail(self):
        some_task = [{
            'url': 'a',
            'params': {'b': 'c'},
        },{
            'url': 'a',
            'params': {'b': 'c'},
        }]

        return self.env["proxy.action.helper"].send_proxy(some_task)

    def button_send_proxy_action_success(self):
        some_task = [{
            "url": "https://jsonplaceholder.typicode.com/posts",
            'params': {'e': 'f'},
        },
            {
            "url": "https://jsonplaceholder.typicode.com/posts",
            'params': {'e': 'f'},
        }]
        return self.env["proxy.action.helper"].send_proxy(some_task)
    #
    # some_task = [
    #     {
    #         "url": "https://jsonplaceholder.typicode.com/posts",
    #         "params": {"param1": 1, "param2": 2},
    #     }
