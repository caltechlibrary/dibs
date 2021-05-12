#  Change log for DIBS

## Version (next)

This version features updated documentation (including an updated [usage guide](https://caltechlibrary.github.io/dibs/) and updated installation instructions) , and the following minor fixes:

* Update the versions of some packages referenced in `requirements.txt`.
* Fix issue #66: missing import in `dibs/people.py`.
* Fix issue #67: `run-server` should check Python version.


## Version 0.3.0

This release features the use of an updated version of the Universal Viewer as well as a new viewer page layout.  We removed the extra HTML around DIB's previous Universal Viewer page and inserted the expiration message and the "end loan" button directly into the Universal Viewer frame, solving several usability issues at once.

Specific issues closed and other changes include the following:
* Fix issues #60, #65: several fixes to the layout of pages and the Universal Viewer on small window sizes and mobile viewers.
* Fix issue #63: avoid briefly showing a "javascript is not enabled" message while the UV page is loading.
* Fix issues #62, #61: fix sorting by the average duration column and handle auto-refresh in such a way that it can be disabled when sorting is in effect.
* Fix issue #55: reduce the number of unnecessary calls to Peewee's `atomic()` handler to avoid needlessly locking the database.
* Fix issue #54: update and bundle a copy of the latest release of the Universal Viewer.
* Fix issue #39: add DIBS version info to the "About" page.
* Fix issue #34: address problems on mobile devices.
* Fix issue #5: move timer display into UV instead of having it in the HTML page outside the viewer.
* Turn off nonfunctional Universal Viewer bookmark icon in the bottom of the frame.


## Version 0.2.1

* Fix issue #51: use a variable to define the help page URL.
* Fix issue #48: use a more systematic approach to printing log statements in the JavaScript console, allow printing to be turned on/off, and leave it off by default for production.
* Fix issue #46: if the user ended a loan through one browser window while having a second browser window open on the same item, the second window would not close the viewer and instead would just show spinning squares for the content.  Now the viewer window actively checks the current loan status.
* Fix issue #45: path to `uv.js` file was not fully qualified.
* Fix issue #43: `people-manager` could get incorrect paths to `htpasswd` and the password file.
* Fix issue #42: browsers were still using cached copies of `/item` page; new code tries to do a beter job of preventing that.
* Fix issue #41: need expire loans before printing them.
* Fix issue #36: null users are not checked for.
* Miscellaneous internal fixes to various parts of the code.


## Version 0.2.0

* The `/stats` page now has shows symbols to indicate recent page retrieval activity, to help gauge how active a given item currently is.
* End times and reloan times are now rounded to whole minutes. This is to help avoid confusing situations where loans seem to go past their allotted times.
* A small new program, `query-dibs`, is available at the top level to query the database from the command line. Currently it has only limited functionality but this will undoubtedly grow over time.


## Version 0.1.1

* When running in debug mode, loan durations and reloan waits are set to 1 minute.
* When _not_ running in debug, loans by staff/library users are not counted in the histories, to avoid skewing the loan statistics.
* Currently active loans are shown in bold face in the `/stats` page.
* When the refresh poll max is reached during auto-refresh on the `/item` pages, a different message is shown to the user alerting them that they need to manually reload the page in order to see updates.
* The `/item` pages should have disabled to the page cache to prevent stale data from being shown to users.


## Version 0.1.0

* Now assumes authentication via Shibboleth or similar scheme is handled by the server. Along with this, it no longer uses sessions.
* Manifest URL rewriting now includes the IIIF version number as part of the base URL pattern that it substitutes. 
* The UV configuration file is now kept in `dibs/static`.
* The `/list` page shows an icond when a manifest is not available for an item and the ready-to-loan buttong is blocked.
* The author column in the `/list` page is now truncated if the author list is very long.
* The default number of rows in the `/list` page is now 50.
* Various small tweaks have been implemented.
* Various problems and bugs have been fixed.


## Version 0.0.4

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
