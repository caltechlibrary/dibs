# Using DIBS

This page describes how DIBS works from the standpoint of the user interface as seen by patrons and staff.  A separate section in this document describes the [system architecture](architecture.html) that implements the functionality described here.


## Authentication

Authentication is assumed to be handled by the system hosting DIBS. In Caltech's case, we use [Shibboleth](https://en.wikipedia.org/wiki/Shibboleth_Single_Sign-on_architecture), an institute-wide, single sign-on system (SSO) for authentication. This means that before users ever reach DIBS, a sign-in page is presented by the web server. The screenshot below shows an example of this:

<figure>
    <img src="_static/media/sso.png">
</figure>

DIBS itself does not do anything beyond distinguishing between regular users and those who have staff privileges (discussed below). This distinction is made based on the identity of the user as conveyed by the SSO system. DIBS does not ask for user login credentials nor store them.


## Front page

The current design of DIBS is focused on helping instructors and students enrolled in classes.  DIBS provides fairly distinct experiences for patrons on the one hand, and staff on the other; this separation is due to expectations about how different classes of users will interact with the system:

1. We expect that patrons will be informed about the availability of specific items via course syllabi or similar resources produced by course instructors.  Consequently, DIBS does not currently expose to patrons a separate index of "all things available for digital loan". In part, this is because we expect patrons will be directly informed about the pages describing individual items, and in part because we anticipate that in the future we will add DIBS links directly to Caltech's [FOLIO](https://www.folio.org)-based catalog.

2. We expect that library staff need to interact with the system in a _different_ way: not to read the materials, but to manage the items in the database of digitized works and control loan parameters.  Thus, staff _do_ see a list of all items available through the system, but access to this list is limited to Library staff.

These considerations explain the front page of DIBS, which (perhaps contrary to expectations) lacks an index or listing of all items in DIBS.  This is because in normal use, we expect that users will go straight either to a page describing an individual item or to a DIBS management page.  The front page acts mainly as an information page that describes the purpose of the system and the loan policies:

<figure>
    <img src="_static/media/welcome-page.png">
</figure>


## The patron experience

As mentioned above, patrons are assumed to be provided information about individual items available for loan.  The working assumption is that they will be given URLs that take them directly to item description pages in DIBS.  An example of such an item description page is shown below:

<figure>
    <img src="_static/media/item-page.png">
</figure>

The item description page provides basic information about a particular title available through DIBS, along with a button to request a digital loan.  The information about the title is derived from Caltech's [FOLIO](https://www.folio.org) server based on the barcode used by Library staff when they add the item to DIBS. 

The text and button shown in the lower half of the page change based on the current availability of the item. The page shows a  <span class="button color-primary">Get loan</span> button if the item is available for loan at that time.  If the item is not available to the patron, the button changes to <span class="button color-not-available">Not available</span>, and in addition, the text above the button provides information about why it is not available and when it will be available again:

<figure>
    <img src="_static/media/item-not-available.png">
</figure>

If the item is available to the user, and they click the <span class="button color-primary">Get loan</span> button, then they will be presented with a brief confirmation dialog.  If they elect to proceed, a loan will be started immediately and they will be transferred to the viewer. The screenshot below gives an example of what a book looks like in this viewer:

<figure>
    <img src="_static/media/loan-in-viewer.png">
</figure>

DIBS uses the [Universal Viewer (UV)](https://universalviewer.io), an open-source browser-based media viewer that works with content described in [IIIF](https://iiif.io/community/faq/) format.  The loan is issued for a limited time, and the end time is shown in the upper left portion of the viewer screen. (The information about the loan duration and the URL for the viewer page are also sent separately via email to the patron, in case they lose it or want to view the content from a different device.)

The patron can elect to end the loan early.  If they do, the viewer will close and they will be presented with a thank-you page that also includes a link to a feedback page:

<figure>
    <img src="_static/media/loan-ended.png">
</figure>

In designing DIBS, we sought to minimize the amount of patron data requested and stored, to maintain patron privacy and reduce the impact of potential data leaks.  DIBS does not store any patron information when a loan is not in effect (after the lock-out period on a title that was just borrowed), and during a loan, it stores only the user's institutional single sign-on (SSO) identity combined with the (single) title they have on loan during the loan period.  There are no provisions in the software for retaining the information past the loan period, or tracking identities or loan statistics based on users.


## The staff experience

Overall, the workflow to add new items to DIBS is simple: staff scan books and store the results in a secure location (one with a shared file system accessible to the DIBS server) and add basic metadata to the DIBS database. Once the item is added to DIBS and flagged as ready to be loaned, a web page for the item allows institutional patrons to request time-limited loans and view the items in the Universal Viewer.  (That is the [patron experience](#the-patron-experience) described in the previous section.)


### How users are identified as staff users

As mentioned [above](#authentication), users are authenticated by a separate software layer before they can access DIBS. This simplifies DIBS's implementation and reduces what it must do to distinguish different user roles.  By default, every authenticated user is assumed to have non-staff privileges, so all that system administrators need to do is tell DIBS which users should have staff privileges. DIBS comes with a command-line utility program called [`people-manager`](../admin/people-manager) for that purpose. (It's located in the [`admin`](.../admin) subdirectory of the DIBS source repository). For example, to add a user with identity `fakeuser2021@caltech.edu` as a staff user, a system administrator needs to run the following command on the server where DIBS is installed:

```sh
admin/people-manager add uname="fakeuser2021@caltech.edu" role="library"
```


### Additional pages available to staff users

Users with staff privileges see additional links in the upper-right hand corner menu on every page presented by DIBS. In particular, the menu provides access to the content list and statistics pages, as shown in the screenshot below:

<figure>
    <img src="_static/media/dropdown-menu.png">
</figure>


### Listing all items in DIBS

Staff are redirected to the main entry point for staff, which is the list page located at `/list`:

<figure>
    <img src="_static/media/list-page.png">
</figure>

As its name implies, the list page provides a list all of the items known to DIBS (whether they are ready to be available for digital loans or not), and allows staff to add, edit, or remove items.  It is also the place where staff can get the link to be distributed to patrons to request loans.  In more detail:

* **Barcode**: the barcode identifying the item in the Caltech Library.
* **Title**: the title of the item.  This is obtained automatically from the LSP (in Caltech's case, FOLIO) based on the item's barcode.
* **Author**: the author of the item.  This is obtained automatically from the LSP (in Caltech's case, FOLIO) based on the item's barcode.
* **Available to loan?**: when unchecked, the item is not made available for digital loans. The presence of a checkbox in this column depends on the state of processing of the document in the scanning workflow; see the section on <a href="#the-scanning-workflow"><i>The scanning workflow</i></a> below.
* **Loan duration**: the duration of a loan, in hours.
* **Copies for loans**: how many copies of the item are being made available for simultaneous borrowing?
* <span class="button color-secondary">Copy link</span>: this copies to the user's clipboard a link to the item loan page.  This is what should be communicated to course instructors, so that they can pass on the URLs to their students.
* <span class="button color-info">Edit entry</span>: edit the entry. This brings up the same form as is used to add new entries, but with the values filled in, allowing the user to change the values and save the results.


### Adding new items

At the bottom of the list page, there are two buttons named <span class="button color-primary">Add new item</span> and  <span class="button color-danger">Manage item list</span>.

<figure>
    <img src="_static/media/bottom-of-list-page.png">
</figure>

If the user clicks the <span class="button color-primary">Add new item</span> button, they are presented with the following screen:

<figure>
    <img src="_static/media/add-item-page.png">
</figure>

Here, information can be entered to describe a new item to be made available for digital loans. Staff only need to enter the item's barcode, the duration of a loan, and the number of copies of the item to be made available via DIBS.  Optionally, they can add internal notes as free-form text, and also, upload a custom cover image. (If the cover image is left off, DIBS will automatically try to find an image based on the ISBN obtained from the LSP.)

Note the only item-specific information needed is the barcode.  All of the metadata shown about an item on other pages (such as the title, the authors, ISBN, etc.) is based on the barcode and obtained by looking up the item barcode LSP.


### Editing existing items

As mentioned above, every item on the [list page](#listing-all-items-in-dibs) has a button named <span class="button color-info">Edit entry</span> next to it. Clicking on this button shows a page essentially identical to the page for adding a new item, except now the fields in the form are filled in with values from the existing item being edited.

<figure>
    <img src="_static/media/edit-item-page.png">
</figure>

As you might have guessed, staff can modify entries by editing these values and then clicking the  <span class="button color-primary">Save</span> button to save the changes to the database.

The edit page also provides the ability to replace the item's cover image, or to delete it altogether. When there is an existing thumbnail image, the page shows the image with a small red trashcan icon overlaid on top of it in the bottom right corner. Clicking this trashcan icon will delete the existing thumbnail image file. On the other hand, clicking the "Choose file" button under the field heading _Replace cover image_ allows a staff user to upload an image from their computer's hard drive; after clicking the <span class="button color-primary">Save</span> button, the uploaded image will become the new cover image for the item.


### Managing the list of items

If the user clicks the <span class="button color-danger">Manage item list</span> button, they are presented with the following screen:

<figure>
    <img src="_static/media/manage-item-list-page.png">
</figure>

In the current version of DIBS, this page only implements two actions. One of them is the ability to remove items from the DIBS database. Clicking the <span class="button color-danger">Delist</span> button next to an item in the list removes the entry for the item in the DIBS database. (However, it does _not_ remove the manifest, scans, or other files &ndash; it only affects the database entry.)

The second feature on the management page is a button near the bottom named <span class="button color-info">Download item list</span>. This button allows staff to download the complete list of items known to DIBS, in [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) format.

<figure>
    <img src="_static/media/manage-items-page-buttons.png">
</figure>

DIBS does not currently have a facility to upload lists of items in (e.g.) CSV format. A future enhancement may bring this capability. Currently, the only way to add items to DIBS is via the web interface, or command-line tools on the server.


### Viewing loan statistics

DIBS offers some basic statistics on the _stats_ page:

<figure>
    <img src="_static/media/stats-page.png">
</figure>

Any items currently on loan will be shown in bold face in the list. In addition, the page reports three statistics in the last three columns of the table.

* _Total loans to date_: this is a straight count of the number of times the item has been loaned and returned. (Currently on-loan items are not added to the count until they are returned.)

* _Average loan duration_: the mean duration of all loans for the item. If the item has never been borrowed, it is reported as "(never borrowed)", otherwise a duration is given in general human-understandable terms.

* _Content retrievals_: this column contains a small bar graph for each item, expressing the number of page retrievals for that item within the past 15, 30, 45 and 60 minutes.  The counts change over time in a rolling fashion and are recomputed relative to the present time every time the page is refreshed. The values are intended to give a rough sense of the reader activity over the past hour for a given item.

The bottom of the stats page also offers a button named <span class="button color-info">Download history</span>, as shown in the screenshot below. When clicked, this will cause the complete loan history to be downloaded to the user's computer in [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) format.

<figure>
    <img src="_static/media/stats-page-buttons.png">
</figure>

Although it's true that the DIBS stats page offers only very basic loan statistics, the ability to download the loan history in CSV format means that users can generate additional statistics and visualizations based on the raw data. 


## The scanning workflow

Before a new item is to be made available through DIBS, it normally requires a workflow to be completed. This workflow involves steps such as scanning book pages, converting the scan images to a format suitable for IIIF, and more. DIBS supports this process in the following way.

1. After an entry is created for a new item as <a href="#adding-new-items">described above</a>, if no IIIF manifest exists yet for that entry, then DIBS shows a button named <span class="button color-primary">Process</span> in the column titled **Available to loan?** as shown in the figure below.  When this button is pressed, an indicator file is created in a location where the document processing workflow looks for it.  Staff do not have to press this button immediately: they can add an entry to DIBS and continue scanning pages until they are done.  Once scanning is completed and the item is ready to be converted to IIIF format, then that is when staff should press the  <span class="button color-primary">Process</span> button.  <figure><img src="_static/media/process-button.png"></figure>
2. Once it is initiated, the workflow runs independently and externally to DIBS and takes time to complete. Until the workflow completes or is interrupted, DIBS shows an hourglass icon in the  **Available to loan?** column of the list page:  <figure><img src="_static/media/item-processing-hourglass.png"></figure>
3. If an error occurred during processing, the hourglass icon will change to a stop sign, as shown in the figure below. The error symbol is for notification purposes only; DIBS does not provide an interface to take additional actions, because the underlying problem is expected to be detected by the workflow system and appropriate measures are assumed to be taken automatically outside of DIBS.  <figure><img src="_static/media/item-processing-problem.png"></figure>
4. Once the workflow process has completed and a manifest file is available for the item, then the item gains the availability checkbox.  <figure><img src="_static/media/item-availability-checkbox.png"></figure>
