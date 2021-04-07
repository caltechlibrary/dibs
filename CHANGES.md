Change log for DIBS
===================

Version (next)
--------------

* The `/stats` page now has shows symbols to indicate recent page retrieval activity, to help gauge how active a given item currently is.
* End times and reloan times are now rounded to whole minutes. This is to help avoid confusing situations where loans seem to go past their allotted times.
* A small new program, `query-dibs`, is available at the top level to query the database from the command line. Currently it has only limited functionality but this will undoubtedly grow over time.


Version 0.1.1
--------------

* When running in debug mode, loan durations and reloan waits are set to 1 minute.
* When _not_ running in debug, loans by staff/library users are not counted in the histories, to avoid skewing the loan statistics.
* Currently active loans are shown in bold face in the `/stats` page.
* When the refresh poll max is reached during auto-refresh on the `/item` pages, a different message is shown to the user alerting them that they need to manually reload the page in order to see updates.
* The `/item` pages should have disabled to the page cache to prevent stale data from being shown to users.


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
