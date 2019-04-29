.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Product Category Sort
======================

This module adds a view to sort your product categories.

Installation
============

Just install the module

Configuration
=============

No configuration required

Usage
=====

Go to you Sale > Configuration > Product Categories & Attributes > Sort Category

Known issues / Roadmap
======================

It's slow ! Indeed when we change the sequence the js client do a call for each category
as we need to be consistant we have to reompute the parent left/right after each write
We should review the way the js send the new sequence in order to have only one call

Credits
=======

Contributors
------------

* Sébastien BEAU <sebastien.beau@akretion.com>
