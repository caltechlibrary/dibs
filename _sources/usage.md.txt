# Using DIBS

This page describes how DIBS works from the users' standpoint.  A separate section in this document describes the [system architecture](architecture.html#architecture--page-root) that implements the functionality described here.


## Guiding assumptions

The current design of DIBS is focused on helping instructors and students enrolled in classes.  DIBS provides fairly distinct experiences for patrons on the one hand, and staff on the other; this separation is due to expectations about how different classes of users will interact with the system:

1. We expect patrons to be mainly students enrolled in educational courses at Caltech.  We expect that patrons looking for materials to borrow will be informed about the availability of specific items via course syllabi or similar resources produced by course instructors.  Consequently, DIBS does not currently expose to patrons a catalog of "all things available for digital loan via DIBS"; in part, this is because such a list was not judged to be useful for DIBS's use-cases, and in part to avoid potential decreased availability of titles due to non-students browsing and borrowing items.
2. We expect that library staff need to interact with the system in a quite different way: to add new items to the database of digitized works and control loan parameters.  Thus, staff _do_ see a list of all items available through the system, but access to this list is limited to Library staff.

These considerations explain the front page of DIBS, which (perhaps contrary to expectations), lacks a login interface or a list of titles available in the system:

<figure>
    <img src="_static/media/welcome-page.png">
</figure>


## The patron experience






## The Library staff experience
