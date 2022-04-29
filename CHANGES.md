#  Change log for DIBS<img width="70em" align="right" src="https://github.com/caltechlibrary/dibs/raw/main/docs/_static/media//dibs-icon.png">

## ★ Version 0.5.4 ★

The changes in this version are purely internal and do not affect functionality or templates.
* New [Flake8](https://flake8.pycqa.org/en/latest/) project config file `.flake8`.
* Minor adjustments to most code files based on Flake8 output.
* Updated `requirements.txt` uses new versions of some Python libraries.
* Minor internal code improvements.


## ★ Version 0.5.3 ★

This version only updates `requirements.txt` to use newer versions of certain libraries, notably Pillow to address a [security issue in that package](https://github.com/advisories/GHSA-9j59-75qj-795w).


## ★ Version 0.5.2 ★

This version fixes a [bug reported (with a fix) by @dlasusa](https://github.com/caltechlibrary/dibs/issues/93) involving incorrect time zone locale handling in the viewer interface, and also bumps up the required version of [Pillow](https://pypi.org/project/Pillow/) to address [several security vulnerabilities](https://github.com/caltechlibrary/dibs/security/dependabot/3) flagged by Dependabot. It also updates a number of other dependencies in `requirements.txt` to their latest versions.


## ★ Version 0.5.1 ★

This version fixes an issue wherein trying to add an item that had an incomplete records in the LSP would result in a misleading error about the item being not found at all.


## ★ Version 0.5.0 ★

This version brings significant changes and new features, but it is also not fully backward compatible with previous versions. We apologize for breaking backward compatibility; we lack the resources to do it differently or create a proper migration engine. If you installed a previous version of DIBS, updating to this new version will, unfortunately, require some work (but hopefully not too much!).

### Breaking changes

* The database object models have changed, and **previous DIBS database files will not work without migration**. Migrating a pre-version-0.5 database file is not difficult and instructions for migrating existing databases are provided in the [wiki for the project on GitHub](https://github.com/caltechlibrary/dibs/wiki).
* The **format of the `settings.ini` file has changed**, as part of the DIBS enhancement to support FOLIO. The old format used a single section called `[settings]`; the new format replaces `[settings]` with a section called `[dibs]`, and adds additional sections for TIND and FOLIO. If you attempt to run the new version of DIBS without updating `settings.ini`, DIBS will either exit with an explicit error or fail to find variable values (which will be a clue that the problem is the changes to the settings file).
* Some of the **HTML template pages have changed**. If you previously installed DIBS and modified the templates to adapt them to your site, it will be necessary to inspect the new templates and figure out how to make the corresponding changes in the new version of DIBS. A normal `diff` between the old and new `dibs/templates`  directories will help, and the changes are limited to only some files (and then mostly to the logic and not the layout components).


### New features

* Supports the [FOLIO](https://www.folio.org) LSP in addition to [TIND](https://tind.io) ILS. Along with this, the updated configuration file `settings.ini-example` has a number of changes relative to existing `settings.ini` files.
* Provides a mechanism for triggering a workflow to convert scans to IIIF format when a new item is added to DIBS. The interface is part of the item list page (`/list`) and involves the addition of a button and some page logic. Along with this, there is a new `settings.ini` variable that tells the server the location of a subdirectory where it should read and write workflow status files.
* Provides the ability to replace the thumbnail image of book covers, in case the automatic algorithm for finding cover images finds an incorrect one or none at all. Along with this, the item editing page (`/edit`) has been reorganized and a new element has been added. Finally, along with this change, there is a new `settings.ini` variable that tells the server the location of a subdirectory used to store thumbnail image files.
* Supports downloading the DIBS item list and loan history as CSV files. Buttons for downloading these are available from the management page and the stats page, respectively.
* Provides a mechanism for showing a site banner for announcements. The banner text can be written to a file in the DIBS server root directory.
* Includes a new helper program, `admin/export-data`, for exporting the data from a DIBS database. **This program works with previous versions of the DIBS database too**, not just the new format in 0.5.
* Includes a new helper program, `admin/set-server-permissions`, for setting the permissions on server subdirectories and files, to help configure a new DIBS installation.
* `admin/run-server` now allows the use of the `--debug-user` flag in all modes, for more debugging capabilities.


### Other changes

* Administrative scripts such as `run-server` have been relocated to a new subdirectory named `admin`.
* The default `manifest` subdirectory and the new subdirectories for the IIIF workflow (by default, `processing`) and cover image thumbnails (by default, `thumbnails`) have been relocated to a new subdirectory named `data`. (However, the settings file controls where the server looks for these subdirectories, and DIBS installations do not have to use the default locations in practice.)
* The database file (by default named `dibs.db`) has also been relocated to the `data` subdirectory by default.
* The versions of many dependencies in the file `requirements.txt` have been updated, and `requirements.txt` now pins the version numbers of dependent libraries to exact version numbers instead of using "this version or later" definitions.
* Hardwired references to TIND.io have been removed.
* Added [Pokapi](https://github.com/caltechlibrary/pokapi) and [Coif](https://github.com/caltechlibrary/coif) as new dependencies for FOLIO interface.
* Titles coming via LSP metadata lookups are now truncated at `:`, `;` and `.` characters in the title, and addition, titles are truncated at 60 characters, to avoid very long title/subtitle combinations.
* The publisher is shown as an additional metadata field in the item view page.
* Fixed issue #90: character encoding was not specified when reading manifest files, causing garbled characters to appear in the IIIF viewer. (Thanks to @stanonik for the report and fix.)
* Fixed issue #89: the Process button would sometimes reappear if the process workflow took too long between steps.
* Fixed issue #88: wrong default set for the item processing directory by `server.py`.
* Fixed issue #87: don't hardcode TIND URLs in `server.py`.
* Fixed issue #86: save cover image thumbnails locally instead of only URLs to external web pages, to avoid the situation where the external site is unresponsive at run time. (This happened to us during demos.)
* Fixed issue #83: provide a way to save and reload database.
* Fixed issue #82: provide a notes field for writing internal text notes about items.
* Fixed issue #78: store the URL to an item page in the `Item` data objects, instead of constructing them at run-time.
* Fixed issue #77: provide info about how to set up a IIIF server.
* Fixed issue #68: make `run-server` allow defining a debug user in all modes.
* Fixed issue #64: don't hardcode TIND URLs in `item.tpl`.
* Fixed issue #40: add a site announcement mechanism.
* Add `CITATION.cff` file.
* Various other bugs fixed, minor refactoring, and other internal changes.
* Documentation has been updated.


## ★ Version 0.4.1 ★

* Fix issue #85: remove email address from server log message printed during status checks
* Expand explanations (in the README and the docs) of what you need to run DIBS at another institution.
* Updated system diagram in the documentation.


## ★ Version 0.4.0 ★

This version implements an interface for starting the IIIF image processing workflow. This is implemented in the `dibs/templates/list.tpl` template file, with an an addition to `settings.ini`. It interacts with the "available" column in the `/list` page.

Other changes and issues fixed:

* Fix issue #81: anonymize user names in trace/debug logs.
* Fix issue #75: allow force-viewing item pages; this uses a query parameter to the item page URL.
* Fix issue #71: add interface to trigger IIIF processing workflow.
* The size of the LRU cache for IIIF images is configurable using variable in `settings.ini`.
* Tweak some user interface elements.
* Take out "Caltech" from email template, to make it more generic.
* Refactor some internal code to further simplify the logic.
* Fix more miscellaneous bugs.
* Do some housekeeping on files.


## ★ Version 0.3.1 ★

This version features updated documentation (including an updated [usage guide](https://caltechlibrary.github.io/dibs/) and updated installation instructions) , and the following minor fixes:

* Update the versions of some packages referenced in `requirements.txt`.
* Fix issue #66: missing import in `dibs/people.py`.
* Fix issue #67: `run-server` should check Python version.


## ★ Version 0.3.0 ★

This release features the use of an updated version of the Universal Viewer as well as a new viewer page layout.  We removed the extra HTML around DIB's previous Universal Viewer page and inserted the expiration message and the "end loan" button directly into the Universal Viewer frame, solving several usability issues at once.

Specific issues closed and other changes include the following:
* Fix issues #60, #65: several fixes to the layout of pages and the Universal Viewer on small window sizes and mobile viewers.
* Fix issue #63: avoid briefly showing a "JavaScript is not enabled" message while the UV page is loading.
* Fix issues #62, #61: fix sorting by the average duration column and handle auto-refresh in such a way that it can be disabled when sorting is in effect.
* Fix issue #55: reduce the number of unnecessary calls to Peewee's `atomic()` handler to avoid needlessly locking the database.
* Fix issue #54: update and bundle a copy of the latest release of the Universal Viewer.
* Fix issue #39: add DIBS version info to the "About" page.
* Fix issue #34: address problems on mobile devices.
* Fix issue #5: move timer display into UV instead of having it in the HTML page outside the viewer.
* Turn off nonfunctional Universal Viewer bookmark icon in the bottom of the frame.


## ★ Version 0.2.1 ★

* Fix issue #51: use a variable to define the help page URL.
* Fix issue #48: use a more systematic approach to printing log statements in the JavaScript console, allow printing to be turned on/off, and leave it off by default for production.
* Fix issue #46: if the user ended a loan through one browser window while having a second browser window open on the same item, the second window would not close the viewer and instead would just show spinning squares for the content.  Now the viewer window actively checks the current loan status.
* Fix issue #45: path to `uv.js` file was not fully qualified.
* Fix issue #43: `people-manager` could get incorrect paths to `htpasswd` and the password file.
* Fix issue #42: browsers were still using cached copies of `/item` page; new code tries to do a better job of preventing that.
* Fix issue #41: need expire loans before printing them.
* Fix issue #36: null users are not checked for.
* Miscellaneous internal fixes to various parts of the code.


## ★ Version 0.2.0 ★

* The `/stats` page now has shows symbols to indicate recent page retrieval activity, to help gauge how active a given item currently is.
* End times and reloan times are now rounded to whole minutes. This is to help avoid confusing situations where loans seem to go past their allotted times.
* A small new program, `query-dibs`, is available at the top level to query the database from the command line. Currently it has only limited functionality but this will undoubtedly grow over time.


## ★ Version 0.1.1 ★

* When running in debug mode, loan duration and reloan waits are set to 1 minute.
* When _not_ running in debug, loans by staff/library users are not counted in the histories, to avoid skewing the loan statistics.
* Currently active loans are shown in bold face in the `/stats` page.
* When the refresh poll max is reached during auto-refresh on the `/item` pages, a different message is shown to the user alerting them that they need to manually reload the page in order to see updates.
* The `/item` pages should have disabled to the page cache to prevent stale data from being shown to users.


## ★ Version 0.1.0 ★

* Now assumes authentication via Shibboleth or similar scheme is handled by the server. Along with this, it no longer uses sessions.
* Manifest URL rewriting now includes the IIIF version number as part of the base URL pattern that it substitutes. 
* The UV configuration file is now kept in `dibs/static`.
* The `/list` page shows an icon when a manifest is not available for an item and the ready-to-loan button is blocked.
* The author column in the `/list` page is now truncated if the author list is very long.
* The default number of rows in the `/list` page is now 50.
* Various small tweaks have been implemented.
* Various problems and bugs have been fixed.


## ★ Version 0.0.4 ★

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
