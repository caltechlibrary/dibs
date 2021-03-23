Change log for DIBS
===================

Version 0.0.3
-------------

* Rewrite manifests to make image accesses go through a new endpoint, `/iiif`, to enable us to better implement access policies.
* Include the time zone in the data/time values we print to the user.
* Don't print "edition" field in item pages if there is no edition info for the item.
* Make the staff login page print an error message for unrecognized user/password combinations.
* Put rate limit on number of possible failed login attempts.
* Add more variables to `settings.ini`, particularly with respect to session handling.
* Use atomic database transactions for certain steps.
* Simplify `dibs_application` in [`adapter.wsgi`](adapter.wsgi).
* Fix various mistakes, refactor some code, and simplify some things.
