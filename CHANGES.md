Change log for DIBS
===================

Version 0.0.3
-------------

* Include the time zone in the data/time values we print to the user.
* Don't print "edition" field in item pages if there is no edition info for the item.
* Use atomic database transactions for certain steps.
* Simplify dibs_application in adapter.wsgi.
* Fix various mistakes in server.py and simplify some code.
