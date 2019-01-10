.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Mail Via
==============

When importing email from incomming gateway and sending back them to follower.
Odoo set in the original sender in the from message. With email provider like mailjet, the mail is not accepted as we do not have the right to send an email with the original sender.

This module will change the FROM with a "via" address and use as name the name with the email of the sender

Contributors
------------

* Sébastien BEAU <sebastien.beau@akretion.com>

