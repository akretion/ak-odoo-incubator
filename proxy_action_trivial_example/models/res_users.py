
from odoo import api, models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    def button_send_proxy_action_fail(self):
        act1 = {
            'url': 'https://httpbin.org/post',
            'params': 'something',
        }
        act2 = {
            'url': 'az',
            'params': 'something'
        }
        acts = [act1, act2]
        return self.env['proxy.action.helper'].send_proxy(acts)

    def button_send_proxy_action_success(self):
        act1 = {
            'url': 'https://httpbin.org/post',
            'params': 'something'
        }
        acts = [act1]

        return self.env['proxy.action.helper'].send_proxy(acts)