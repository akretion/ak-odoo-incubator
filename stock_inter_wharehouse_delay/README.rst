.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=====================
Inter Warehouse Delay
=====================

Manage delay between warehouses.
Set in one place how many days it takes to move goods
from one warehouse to another one.
This delay will be then writed on the according rules.

It will allow to have a WH0:Picking OUT one day and
 a WH1:Picking IN few days after.


Usage
=====
Go to Inventory > Warehouse Management > Warehouse,
Specify a partner per warehouse.

Go to Inventory > Global Procurement Rule, 
check your interwarehouse rules(*) have a partner set in Partner Address

Go to Inventory > Warehouse Management > Inter Warehouse
Create a record per Sender WH -> Reciever WH with a delay.

(*)interwarehouse rules are usually named
"WH1: Stock -> My Company:Transit Location"


Known issues / Roadmap
======================

* 

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.

Contributors
------------

* Raphaël Reverdy <raphael.reverdy@akretion.com> (Akretion)

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* Akretion


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
