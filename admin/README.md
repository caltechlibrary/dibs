# Admin utilities for DIBS

This directory contains a number of small administrative utilities for DIBS. Their purposes are summarized below. Some of them are described in the [user manual](https://caltechlibrary.github.io/dibs), in the sections on installation and usage.

## Table of Contents

* [`export-data`](#export-data-export-data-a-dibs-database)
* [`import-data`](#import-data-import-data-into-a-dibs-database)
* [`load-mock-data`](#load-mock-data-load-some-sample-data-for-dibs)
* [`loan-manager`](#loan-manager-perform-administrative-functions-on-loans)
* [`people-manager`](#people-manager-manage-user-roles-in-dibss-people-table)
* [`run-server`](#run-server-start-a-local-dibs-server-for-testing)
* [`set-server-permissions`](#set-server-permissions-set-essential-directory-permissions)
* [`test-token`](#test-folio-token-check-the-folio-token-is-still-valid)
* [`update-item-data`](#update-item-data-update-item-records-with-current-values-from-lsp)


## `export-data`: export data a DIBS database

This program reads a DIBS database file and, based on the options given on the command line, writes one or more files containing the contents of one or more tables from the DIBS database.  Each table holds a different kind of model instance, such as `Item`, `History`, etc.  The default action is to put all the files into one ZIP archive as the output. You can run this program with the `-h` option to get more information about its usage.

This program and `import-data` (below) can be useful for migrating servers, backups, and other situations where you want to get the data out of (and possibly back into) the DIBS database.


## `import-data`: import data into a DIBS database

This program is the opposite of `export-data`;  takes a ZIP archive of JSON files previously exported by `export-data` (above), and loads a DIBS database using that data. The ZIP archive must contain 4 files corresponding to the 4 database object tables in a DIBS database. The path to the archive file is expected to be the last argument on the command line. You can run it with the `-h` option to get more information about its usage.


## `load-mock-data`: load some sample data for DIBS

When first starting out with DIBS, for testing purposes, you may want to add some sample data. The program `load-mock-data` can be used for this purpose. It takes no arguments and is intended to be run from the DIBS directory root:
```sh
admin/load-mock-data
```


## `loan-manager`: perform administrative functions on loans

This program can be used to perform some loan management functions on a DIBS server. Currently, it offers functions for listing active and recent loans, as well as forcefully ending active loans on a given item. You can run it with the `-h` option to get more information about its usage. For example:
```sh
admin/loan-manager --list-loans
```


## `people-manager`: manage user roles in DIBS's people table

This administrative utility lets you simultaneously (1) add/remove/edit people's roles in DIBS's people table, and (2) do the same in a password file used for Apache basic auth (if you use that).

### Background: authentication and access control in DIBS

There are 2 layers of access control in DIBS when deployed in a web server:

1) can an incoming user access any part of DIBS at all?
2) can the user access staff pages, or only patron pages?

Layer #1 is implemented in the web server environment, and the details of how it's done depends on the specifics of the installation.  As far as DIBS is concerned, it only cares about whether a user has been authenticated or not.  When a page or API endpoint is requested from DIBS, the request environment given to DIBS by the web server will either include a user identity (if the use has been authenticated) or not.  DIBS simply refuses access to everything it controls if a user identity is not present in the request environment.

Layer #2 is implemented in DIBS itself.  DIBS's database uses Person objects to distinguish between people known to have staff access (i.e., who can access pages like `/list`), and everyone else.  When a request for a page or an endpoint comes in, DIBS looks for the user identifier in the HTTP request environment given to it from the web server, checks if that user is in the Person table, and checks if the user has a role of `library`.  If the role is `library`, access to staff pages is granted; if the Person entry doesn't have a role of 'library', the user is not shown links to the staff pages nor can they access the relevant endpoints.

### Managing users using `people-manager`

One of `people-manager`'s purposes is to add and manage entries in DIBS's Person table.  Only users who should have staff access (i.e., have role `library`) need to be added to the Person table, and in an SSO scenario, that's all you need to deal with.

In an SSO scenario, the management of users in the authentication system is typically handled by another system and possibly another administrative entity at your institution.  In an Apache basic auth scenario, users are listed in a password file managed by the command-line program `htpasswd`, and the Apache server configuration is set up to read this password file.

If you are using Apache basic auth and `htpasswd`, and have enabled the relevant variables in the `settings.ini` file, then `people-manager` will also manage entries in the password file.  Thus, in a basic auth scenario, you can use `people-manager` to simultaneously add/change users and their roles in the password file and make the corresponding changes in DIBS's `Person` table.

Run the program with the option `help` to get a usage summary.


## `run-server`: start a local DIBS server for testing

For local experimentation and development, the script [`run-server`](run-server) can be used to start a local DIBS server on your computer. It looks for a file named `settings.ini` in the current directory or the parent directory, and reads it to set various DIBS configuration variables. The command-line options to run-server can override some of the configuration values in `settings.ini`.

### Run modes

There are 3 run modes available. Two of the modes can be set using the `settings.ini` file, but are overriden via the option `--mode` on the command line.  If no `--mode` option is given, then this program uses the `RUN_MODE` value from `settings.ini`. In addition, this program offers a third run mode only available using the `--mode` option. The possible run modes and their effects are as follows:

*  `normal`: uses the Python `mod_wsgi-express` module without debugging options. The server will run multiple threads, will not reload if source files are changed, will not reload templates if they are changed, and will not stop for exceptions. It looks for a file named `adapter.wsgi` in the current directory and passes it to `mod_wsgi`. This mode is a close approximation to running DIBS in a basic Apache2 `mod_wsgi` environment, with `adapter.wsgi`.

* `verbose`: like normal mode, but will produce detailed logging to the terminal.  This mode is useful for testing DIBS using `adapter.wsgi` in `mod_wsgi`.  Verbose mode is invoked using the option `--mode verbose`, or setting `RUN_MODE` to `verbose` in settings.ini. (Using `--mode verbose` overrides `settings.ini`.)

* `debug`: this uses [Bottle](https://bottlepy.org)'s development server instead of `mod_wsgi-express` and turns on maximum debugging options. This mode does **not** use `adapter.wsgi`. It will turn off template caching, will drop into pdb upon exceptions, and unlike `mod_wsgi-express`, the [Bottle](https://bottlepy.org) server will also automatically reload any changed source files. In addition, the reloan wait time and loan expirations are set to 1 minute (overriding values set on individual items), and finally, the statistics gathering will include loans by staff users. (Normally, staff users are not included in the statistics to avoid skewing the results.) Debug mode is invoked using the option `--mode debug`. It has no corresponding `RUN_MODE` value in `settings.ini`.

Since debug mode uses [Bottle](https://bottlepy.org)'s default server, the normal authentication mechanism is nonfunctional and you will not be able to access most pages _unless_ you define a person using DIBS's `people-manager` script (above) and give them the role of `library`, and then tell `run-server` the identity of that user.  To do this, use option `--user` with the name of the user you defined.  Here is an example of running in debug mode:

```sh
admin/people-manager add uname="debuguser" role="library"
admin/run-server --mode debug --debug-user debuguser
```

This will start a local web server listening on `localhost` port 8080.  You can open a browser window on `http://localhost:8080` and you should see the DIBS welcome page, as well as be able to see the "List" and "Loan statistics" options in the pull-down menu:

<p align="center"><img width="60%" src=".media/dropdown-menu.png"></p>

### Database file, manifests directory, and IIIF server URL

A number of additional command-line options allow you to override values set in `settings.ini`. These are:

* `--database`: override the value of `DATABASE_FILE`
* `--manifests`: override the value of `MANIFEST_DIR`
* `--iiif_url`: override the value of `IIIF_BASE_URL`

Please consult the comments in `settings.ini` or the DIBS documentation for more information about the purpose of these configuration variables.

### Additional options

In a live server, the default base URL for DIBS is normally set by the Apache2 configuration. For the local server started by this program, the default is http://localhost:8080. The option `--base-url` can be used to change this. The value given to `--base-url` should contain the protocol, hostname, port (if needed) and any additional path elements of the root of DIBS on the server; e.g., "https://library.example.edu/dibs". (Note: the path component is ignored when running in debug mode.)

By default, `run-server` looks for a WSGI adapter named `adapter.wsgi` in the current directory. The option `--adapter` can be used to tell `run-server` to use a different file.


## `set-server-permissions`: set essential directory permissions

This program sets certain basic file and directory permissions for a typical server configuration of DIBS.  It only affects a small number of items that will not have the correct permissions after cloning the git repository. The arguments `--owner` and `--group` can be used to choose the owner and group to be used for the permissions.  Normally, this would be the Apache server user and group.  For example, if the user name is "www-data" and the group name is "www-data", then you would run this program as follows:

```sh
admin/set-server-permissions --owner www-data --group www-data
```


## `test-folio-token`: check the FOLIO token is still valid

When using FOLIO as the LSP, DIBS needs to contact FOLIO for metadata when staff add new items to DIBS. FOLIO uses API tokens for authentication, and those tokens eventually get invalidated. When that happens, DIBS calls will fail. Consequently, it's a good idea to periodically test the FOLIO credentials and update the token stored in the `settings.ini` file. The utility `test-folio-token` is useful for that purpose.

Without any arguments, it will simply return a non-zero status number if the credentials are invalid.  If given the `--slack` argument, the value must be in the form _slack-channel:slack-token_; in that case, this program will post a message to the channel if the FOLIO credentials are invalid. Here is an example of a crontab line for daily testing of the FOLIO credentials and posting to a (fake) Slack channel named "my-channel":

```
0 8 * * * /path/to/dibs/admin/test-folio-token --slack my-channel:xoxb-895-asfd123
```


## `update-item-data`: update item records with current values from LSP 

This program reads the DIBS database file, compares every item's metadata fields to the values of the corresponding record in the LSP, displays the differences (if any), and offers to update the DIBS objects to match the LSP records. Example usage:
```sh
admin/update-item-data
```

`update-item-data` can be run on a live server. At Caltech, we wrote this program because our catalog search service (EDS – EBSCO Discovery Service) changed the permalink scheme on multiple occasions, causing the DIBS links to item description pages to become invalid. Since the links are stored in the DIBS database when new items are added, there needs to be a method to update the links as needed. We wrote `update-item-data` for that purpose.
