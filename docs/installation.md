# Installation and operation

On this page, you may wish to follow one of the following paths based to your situation. (Note: the boxes in this diagram are clickable links to the sections in question.)

<div align="center">

```{mermaid}
flowchart TD;
  node1(Preliminary requirements)-->node2(Installation);

  node2-->node3(Configuring DIBS for a local test);
  node2-->node4(Configuring DIBS for multiuser use);

  node3-->node5(Running DIBS in test/debug mode);
  node4-->node6(Running DIBS in production);

  style node1 fill:white, stroke:orange;
  style node2 fill:white, stroke:orange;
  style node3 fill:white, stroke:orange;
  style node4 fill:white, stroke:orange;
  style node5 fill:white, stroke:orange;
  style node6 fill:white, stroke:orange;

  click node1 "/dibs/installation.html#preliminary-requirements" _self;
  click node2 "/dibs/installation.html#installation" _self;
  click node3 "/dibs/installation.html#configuring-dibs-for-a-local-test" _self;
  click node4 "/dibs/installation.html#configuring-dibs-for-multiuser-use" _self;
  click node5 "/dibs/installation.html#running-dibs-locally" _self;
  click node6 "/dibs/installation.html#running-dibs-in-production" _self;
```

</div>

## Preliminary requirements

The core DIBS server is written in [Python 3](https://www.python.org) and makes use of some additional Python software libraries that are installed automatically during the [installation steps](#installation). It also assumes a Unix-like environment (Linux, macOS) and a working Internet connection.

Although DIBS relies on the existence of a IIIF image server, for initial exploration, you _don't_ need to set up a IIIF server &ndash; you can reference content located in any of a number of publicly-accessible IIIF servers around the world, and DIBS includes a sample [IIIF manifest](https://iiif.io/explainers/using_iiif_resources/#iiif-manifest) as an example of doing that. Thus, in principle, all you need to run the DIBS demo is a Unix-like system (Linux, macOS), a Python installation, the DIBS source code, and an Internet connection.

To run a proper DIBS server at another institution (other than [Caltech](https://www.caltech.edu)), certain additional things are needed:

1. A **IIIF server**. At Caltech, we use a [serverless component](https://github.com/nulib/serverless-iiif) running on an Amazon cloud instance, but [many other IIIF server options exist](https://github.com/IIIF/awesome-iiif#image-servers). If you're looking at DIBS, presumably it means you want to serve content that is not freely available in a public IIIF server, which means you will need to set up a server of your own.
2. A **web server** to host DIBS.  The current version of DIBS has only been tested with Apache2 on Linux (specifically, Ubuntu 20) and macOS (specifically 10.14, Mojave). DIBS comes with a [WSGI adapter file](https://github.com/caltechlibrary/dibs/blob/main/adapter.wsgi) adapter file and [sample config file for Apache](https://github.com/caltechlibrary/dibs/blob/main/dibs.conf-example), but it should be possible to run DIBS in other WSGI-compliant servers.
3. An **authentication layer**. DIBS assumes that the web server takes care of user authentication in such a way that DIBS is behind the authentication layer and all users who can reach DIBS pages are allowed to view content. DIBS itself only implements checks to distinguish between regular users versus staff who are allowed to access restricted pages. For the authentication layer, at Caltech we use the [Shibboleth](https://en.wikipedia.org/wiki/Shibboleth_Single_Sign-on_architecture) single sign-on system, but it is possible to use other schemes. For a local server behind firewalls, [Apache Basic Authentication](https://httpd.apache.org/docs/2.4/howto/auth.html) can also be used. The installation and configuration of a single sign-on system depends on the specifics of a given institution, and are not described here.
4. The use of [FOLIO](https://www.folio.org) LSP or [TIND](https://tind.io) ILS for retrieving metadata based on barcodes or unique identifiers, _or_  a willingness to extend the existing metadata retrieval layer in DIBS. We strove to limit dependencies on external systems, but the interface for staff to add items to DIBS requires looking up some limited metadata based on an item's barcode, and lacking a universal scheme to do that, we had to write our own interface layer. The use of another LSP will require extending this interface layer. (Thankfully, the [code is short](https://github.com/caltechlibrary/dibs/blob/main/dibs/lsp.py) and the amount of metadata required is small.)
5. Modification to the HTML templates to change the branding. The template files in [`dibs/templates`](https://github.com/caltechlibrary/dibs/blob/main/dibs/templates) are specific to Caltech, and will need to be edited to suit another installation. (We are open to making the branding customization easier and would welcome a [pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) for suitable changes!)


## Installation

Installing DIBS is simple. It only requires downloading a copy of the software, installing Python software dependencies, and editing a configuration file.  DIBS currently does **not** have separate installation destination &ndash;  running DIBS means running it from the source directory.


### Download a copy of the software

There are several ways of getting the latest release of the DIBS source code. Here is one of the simplest:

1. Go to the [releases page](https://github.com/caltechlibrary/dibs/releases) in the GitHub repository for DIBS.
2. Find the latest release there (normally the first one on the page). <img align="right" width="200px" src="https://github.com/caltechlibrary/dibs/raw/main/.graphics/assets.png"/>
3. Find the **Assets** section of the release.
4. Click on the link titled **Source code** (zip); it will be downloaded.
5. Unzip the file.

The result will be a subdirectory named `dibs`, which contains the source code.  It should look more or less like this:

```
├── CHANGES.md
├── CITATION.cff
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── INSTALL-Python3.md
├── INSTALL.txt
├── LICENSE
├── LICENSE.html
├── Makefile
├── People-Manager.md
├── README.md
├── SUPPORT.md
├── adapter.wsgi
├── admin/
├── codemeta.json
├── data/
├── dev/
├── dibs/
├── dibs.conf-example
├── docs/
├── htdocs/
├── requirements.txt
├── settings.ini-example
├── setup.cfg
├── setup.py
├── tests/
└── viewer/
```


### Install Python dependencies

Assuming that your copy of DIBS is in a subdirectory named `dibs` (as it would be after the previous step), change your shell's current working directory to that directory, and run the following command to install the Python dependencies on your system or your virtual environment:

```sh
python3 -m pip install -r requirements.txt
```


## Configuration

If you are new to DIBS and all you want to do is test drive it, you can follow the instructions in the first subsection below. If you are setting up DIBS for multiuser use, you can [jump ahead to the second subsection](#configuring-dibs-for-real-use).


### Configuring DIBS for a local test

DIBS comes with an example IIIF manifest that uses a public IIIF server operated by the [Wellcome Library](https://wellcomelibrary.org). (Thank you, Wellcome Library!) This makes it possible to run a local copy of DIBS without much effort. Please follow the simple steps below.

#### ① Create the `settings.ini` file

The file `settings.ini-example` is a sample configuration file. For a test run of DIBS, it is enough to simply copy the example to create `settings.ini`:

```sh
cp settings.ini-example settings.ini
```

#### ⓶ Load a sample book into DIBS

Prior to starting the DIBS server for the first time, for testing purposes, you may want to add some sample data. This can be done by running the script [`load-mock-data`](admin/load-mock-data) located in the `admin` subdirectory of the DIBS source code tree.

```sh
admin/load-mock-data
```

#### ⓷ Set a sample user's role

The program [`people-manager`](admin/people-manager) in the `admin` subdirectory is an interface for adding user and role information.  To be able to manage DIBS content, create at least one user with a role of "library".  Suppose you want to name your sample user "dibsuser", then you could run the following command:

```sh
admin/people-manager add role="library" uname="dibsuser"
```


After this, proceed to the section on [Running DIBS locally](#running-dibs-locally) below.


### Configuring DIBS for multiuser use

Setting up an actual server in an institutional setting will require a little bit more configuration work, as well as a IIIF server that you can use.


#### ①  Create and edit the `settings.ini` file

Certain characteristics are configured using a file named `settings.ini`, which DIBS looks for in the `dibs` directory. The file `settings.ini-example` is a sample configuration file for DIBS.  Copy the file to `settings.ini`,

```sh
cp settings.ini-example settings.ini
```

then edit its contents in a text editor to suit your local installation. The comments in the file explain what each of the variables does, but we elaborate on some notable variables below:

* `LSP_TYPE`: When items are added to DIBS via the web form, the system looks up basic metadata about an item in an LSP or ILS. This variable determines the adapter layer used. Currently, the only two options are `folio` or `tind`. Also make sure to **set the corresponding variables in the sections for `[folio]` or `[tind]`**, respectively, near the bottom of the `settings.ini` file.
* `MANIFEST_DIR`: This variable sets the path to the directory where DIBS looks for manifest files.  Each file name should follow the pattern <i><code>N</code></i><code>-manifest.json</code>, where <i><code>N</code></i> is the item barcode.  The source distribution of DIBS comes with a sample manifest for illustration purposes.
* `PROCESS_DIR`: The section on [the scanning workflow](usage.html#the-scanning-workflow) describes the basic scheme that DIBS implements for initiating an external workflow that will convert book scans into the format needed by IIIF.  This scheme involves reading and writing files to the directory indicated by the variable `PROCESS_DIR` in the settings file.  When a new item is added to DIBS from the /list page, a button named <span class="button color-primary">Process</span> is shown next to the new item; when library staff press that button, DIBS writes a file in the `PROCESS_DIR` location and watches for the presence of other files.  The end point of the workflow is assumed to be the appearance of a IIIF manifest for the item in the `MANIFEST_DIR`. f you do not want to use the workflow scheme, leave this value empty; DIBS will skip the <span class="button color-primary">Process</span> button, and will only monitor for the existence of the manifest file.
* `IIIF_BASE_URL`: The value of this variable should have the form `https://youriiifserver.yourdomain.edu/iiif/2`, and it should be the common base for IIIF URLs served by your IIIF server. (This means that the value should appear throughout your manifest files, as the common root of all page images.) This URL will not be shared with clients.  **You should protect this URL from becoming public** if you are making copyrighted works available via DIBS, because knowledge of this URL would allow anyone with familiarity with IIIF to bypass restrictions in DIBS and access your IIIF content directly. When DIBS reads a manifest, it replaces all instances of the value of `IIIF_BASE_URL` with a URL rooted at the DIBS server's address, and this modified manifest is what it serves to clients. When a client requests page images via the translated URL, DIBS reverses the transformation to construct the IIIF URL from where it can get the page image, and then returns that data back to the client. The client never sees the real URL of the IIIF server or the images. The _controlled digital lending_ aspect of DIBS is that it also refuses to return IIIF content unless the client has been authenticated and the user has borrowed the item through DIBS' loan system.
* `MAIL_HOST`, `MAIL_PORT`, `MAIL_SENDER`: When a patron starts a loan, DIBS send send them an email message that summarizes information about the loan, including a link to the viewer page. The destination address for the email message is the sign-on received from the authentication layer.  The variables `MAIL_HOST`, `MAIL_PORT`, and `MAIL_SENDER` set the mail server details used by DIBS. Note that for this to work, the account owning the web server process must be able to send email from the machine where the web server is running to the patrons.
* `FEEDBACK_URL`: After a patron ends a loan, they are taken to thank-you page on which is shown a link to a feedback page. This variable sets the web address of the feedback form. At Caltech, we use a simple Google form with only three questions; you may wish to do something similar, or perhaps use an existing issue tracking/feedback system at your site.
* `RUN_MODE`: This variable takes one of two values: `normal` or `verbose`. In `verbose` mode, DIBS logs debug-level information in the server logs (or the standard output, if being run using the `run-server` program included with DIBS). Patron names/email addresses are anonymized, so there is relatively little privacy risk in running in `verbose` mode in production. It can be very useful to use `verbose` mode while learning how DIBS works, even if you later decide to switch to `normal`.


#### ⓶ Set up authentication for DIBS

The details of this step depend on your particular institutional requirements and local system configuration. If you are using a single sign-on system such as Shibboleth, you may need to do configuration and other steps in your server environment, but it is beyond the scope of this document to explain how that can be done.

If you are setting up a server behind a firewall (perhaps for local development of a new DIBS site, or within some other closed environment) and want to use [basic authentication in Apache](https://httpd.apache.org/docs/2.4/howto/auth.html), take the following steps:

* Uncomment the variables `HTPASSWD` and `PASSWORD_FILE` in your `settings.ini` file, and set them to point to the `htpasswd` program on your system and the file you will use to store encrypted passwords, respectively.
* Enable `AuthType Basic` in your Apache configuration. The location of the configuration file depends on the way Apache is set up on your system; as an example, on our internal development server running on Ubuntu the location is `/etc/apache2/sites-available/apps-le-ssl.conf`. Here's an example of what the configuration can look like:
    ```
    # DIBS comes with an adapter.wsgi file ready to use.
    WSGIScriptAlias /dibs /var/www/sites/dibs/adapter.wsgi
    <Location /dibs>
            AuthType Basic
            AuthName "DIBS"
            AuthBasicProvider file
            AuthUserFile "/var/www/sites/dibs/password.txt"
            require valid-user
    </Location>
    ```

The value of the `AuthUserFile` **must match the path in** `PASSWORD_FILE` used in the DIBS `settings.ini` file.  


#### ⓷ Add staff users

As mentioned above, DIBS needs to distinguish between users who are allowed to perform administrative tasks (such as adding new items for loans and setting loan parameters) and regular users. The program [`people-manager`](admin/people-manager) in the `admin` subdirectory is an interface for telling DIBS about users who have staff privileges.  To be able to manage DIBS content, **create at least one user with a role of `library`**.

If you are using Apache basic auth, `people-manager` will also allow you to add entries (with passwords) to the password file indicated by the `PASSWORD_FILE` variable in DIBS' `settings.ini` file.

The user name must be given as the name used by people in the authentication system (e.g., the SSO sign-on login name, if you use SSO). For example, to make `fakeuser2021@someuniversity.edu` be recognized as having staff privileges, you would run the following command:

```sh
admin/people-manager add role="library" uname="fakeuser2021@someuniversity.edu
```


#### ④ Set permissions on important DIBS directories

A server process such as Apache normally runs with a user identity and group identity that is different from real user accounts on the server computer. This means that the files and directories for DIBS, when they are installed by a user on the computer, may have different ownership and permissions than are needed by the web server process. To make sure that the web server process can read and write to the directories, DIBS comes with a small program to set permissions on certain critical DIBS files and directories. Run this program as shown below, replacing `PROCESS_USER` and `PROCESS_GROUP` with the actual server process user and group (and note the use of `sudo` here):

```sh
sudo admin/set-server-permissions --owner PROCESS_USER --group PROCESS_GROUP
```

For example, on our servers, `PROCESS_USER` and `PROCESS_GROUP` are both `www-data`, so for our installation, the command uses the arguments `--owner www-data --group www-data`.

Note: make sure to **run `set-server-permissions` after running `people-manager`** for the first time, so that `set-server-permissions` can set the permissions on the DIBS database file. 


#### ⑤ Set up your IIIF server

A fully functioning DIBS installation requires a IIIF server where you put content to be served via DIBS. A final step is thus to set up a IIIF server for DIBS' use. The instructions for doing so depend on the specific server used &ndash; please refer to the relevant documentation for whatever IIIF server you are using.


## Running DIBS

You can run DIBS on your local computer for initial exploration and testing, as well as during development and customization of DIBS. This is easy to do using the `run-server` program provided with DIBS. On the other hand, running DIBS on a real server, for actual use by patrons at your institution, requires the use of a full web server environment and other components. Both cases are described below.


### Running DIBS locally

For local experimentation and development, the script [`run-server`](run-server) can be used to start a built-in web server on your computer. Since a local environment will not have the authentication layer normally assumed by DIBS, you need to tell the built-in web server who to pretend to be. For example, if you used `people-manager` to add a user named "dibsuser" as [described in the section on configuration](#configuring-dibs-for-a-local-test), then you can start the local server in debug mode like this:

```sh
admin/run-server --mode debug --debug-user dibsuser
```

This will start a local web server listening on `localhost` port 8080.  Open a browser window on `http://localhost:8080` and you should see the DIBS welcome page, as well as be able to see the "List" and "Loan statistics" options in the pull-down menu:

<div style="width:70%; margin-left: auto; margin-right: auto">

![Welcome page](_static/media/dropdown-menu.png)

</div>

If you cannot access the welcome page, check the shell window for any messages that may provide clues about what went wrong. If you can see the page but do not have the "List" and "Loan statistics" items in the menu, then it means that there is a mismatch between the current user as set by the `run-server` command line ("dibsuser" in our example here) and the roles configured in DIBS using `people-manager`. Check that [the step described earlier](#load-a-sample-user-into-dibs) has been performed and the same user names are used in both places.

Using the `debug` run mode changes the behavior of `run-server` in various useful ways. For example, it will automatically reload source files if any of them are edited. If you will be doing anything with DIBS such as editing the HTML templates, running with `--mode debug` is highly recommended.


### Running DIBS in production

Note that `run-server` is **not intended for use in production servers**. For actual use, you must configure a web server such as [Apache](https://httpd.apache.org) to host the system. DIBS comes with an [`adapter.wsgi`](adapter.wsgi) and an example [Apache conf file](dibs.conf-example) for this purpose to help you get started. The latter file configures the web server and tells it to use `adapter.wsgi` (also provided with DIBS) to define a WSGI application for DIBS.

To start DIBS in this environment, you most likely need to restart the Apache process on your system. 
