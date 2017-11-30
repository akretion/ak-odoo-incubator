web_search_debounce
===================

Delay the search in autocomplete (many2one) until the user stop typing.

Without this module :

A search request (AJAX call) is made after each key entered in the input.
Useless requests/responses for both the server and the user.

With this module : 

A search request is made when the user stop typing. (default 800 ms).
Less useless requests/responses are made.


Roadmap / TODO
--------------

* On first run, it will wait instead triggering search with ""


Contributors
------------

* haprfr Akretion

Maintainer
----------

Akretion
