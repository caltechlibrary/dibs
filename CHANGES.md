Change log for DIBS
===================

Version 0.1.0
-------------

* Now assumes authentication via Shibboleth or similar scheme is handled by the server. Along with this, it no longer uses sessions.
* Manifest URL rewriting now includes the IIIF version number as part of the base URL pattern that it substitutes. 
* The UV configuration file is now kept in `dibs/static`.
* The `/list` page shows an icond when a manifest is not available for an item and the ready-to-loan buttong is blocked.
* The author column in the `/list` page is now truncated if the author list is very long.
* The default number of rows in the `/list` page is now 50.
* Various small tweaks have been implemented.
* Various problems and bugs have been fixed.


Version 0.0.4
-------------

* Rewrite manifests to make image accesses go through a new endpoint, `/iiif`, to enable us to better implement access policies.
* Include the time zone in the data/time values we print to the user.
* Don't print "edition" field in item pages if there is no edition info for the item.
* Make the staff login page print an error message for unrecognized user/password combinations.
* Put rate limit on number of possible failed login attempts.
* Add more variables to `settings.ini`, particularly with respect to session handling.
* Track history of loans on items and provide a statistics page at `/stats` to display the results. (No user data is saved.)
* Use atomic database transactions for certain steps.
* Simplify `dibs_application` in [`adapter.wsgi`](adapter.wsgi).
* Refactor internal database code and server code.
* Make many small enhancements and changes to various web pages.
* Fix various mistakes, refactor some code, and simplify some things.
