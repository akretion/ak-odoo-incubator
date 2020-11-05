I believe we should strongly refactore this module on migration.
1) Being able to choose a different account depending on the delivery carrier having the same carrier type .
(for geodis carrier type we have calberson and france express which need a différent account...)
It should be done in delivery_roulier_geodis so this module can work out of the box.
=> many2many between carrier account and delivery carrier
in roulier_get_account, define a _get_account_domain. and add a domain of this form : ['|', ('delivery_methods', '=', False), ('delivery_method', '=', self.carrier_id.id)]


2) beeing able to choose a different account depending on the shop. 
=> This one could stays in this module and do the same as 1 but with shop : add domain : ['|', ('shop_id', '=', False), ('shop_id', '=', self.shop_id.id)]

This way this module will work with no conflict even it will ease tests of custom modules..
=> Allow  us to remove the post_init_hook...
