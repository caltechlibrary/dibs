
# People Manager

DIBS is intended to be used with a single sign-on system
(SSO) but there remains a need to create and manage access
to service accounts outside of SSO. This includes assigning
application level roles while still using SSO for authentication.

Since modifing user access is an infrequent activity managing
people associated with the DIBS web application is handled through
a simple command line tool. This minimized the need for either
exposing user management to the web (removing an attack serface).
On the backend CLI are easy to build and require minimal support
as they are used by system administrative staff.

## Person Data Model

DIBS supports a simple Person data model. It consists of the following
attributes.

uname
: The username, e.g. email addresss, associated with accessing DIBS

secret
: If SSO is not being used this is that password used to authenticate.
a empty password means the account is disabled unless SSO is used.

display_name
: The display name on screen, e.g. "Jane Doe"

role
: This is text string used to assocated a role. Initially there is
one role allowing administrative access and that role is "library".
If the role field is an empty string no role is assigned so patron
is emplied.

updated
: This is a timestamp of when the Person object was last updated

No additional information is stored in the Person model. This is
based on all identifying information becoming toxic over time.
Ideally only library staff are included in the person table holding
the Person module data. If SSO is used for library staff then no
password needs to be stored in the person table removing one more
angle of attack and data toxicity.

## Adding People

The "add" verb tells the people manager cli you want to add
someone to the person table. The minimum field required is
the "uname".  You many also provide the remaining model fields
at the same time.  Here is an example of adding a user name
"Jane M. Doe" with a username of "janedoe", and role of "library".

```sh
./people-manager add \
    uname=janedoe \
    display_name="Jane M. Doe" \
    role="library"
```

NOTE: there is no space between the key, equal sign and value.

If you want to include setting a password without typing it on the
command line then leave the value empty.  This is how to create
the Jane Doe account with a password (you will be prompted to
type the password before the command completes).

```sh
./people-manager add \
    uname=janedoe \
    display_name="Jane M. Doe" \
    role="library" \
    secret=
```

If you wanted to create a full Person module and be prompted
for each field you could type the command as

```sh
./people-manager add \
    uname= \
    display_name= \
    role= \
    secret=
```

You would then be prompted for each value individually (sorta
like the Linux `adduser` command).


## Listing People

DIBS provided the command line program `people-manager` to manage
the Person objects in the system.  To list the people defined in
DIBS use the "list" verb.

```sh
./people-manager list
```

To list an inidividual person you need to know their "uname".
If I want to look up the user with a uname of "janedoe" I would
do so by adding the "uname" key value pair on the command line.

```sh
./people-manager list uname=janedoe
```

NOTE: the secert field is **not** displayed.

## Updating People

You can update model attributes individually. Use the "update" verb
instead of "add". This will update an existing Person model. The uname
value can not be changed but all other attributes can be changed. If
you need to change the uname value then add a new record and remove the
old one.

Updating the display name for `janedoe` to "Jackie Doe".

```sh
./people-manager update uname=janedoe \
    display_name="Jackie Doe"
```

Or to prompt for the display name attribute.

```sh
./people-manager update uname=janedoe \
    display_name=
```


## Removing People

To remove a person from the person table you need to know their uname.
The verb to remove someone is "remove". To remove janedoe from the
table you would do the following.

```sh
    ./people-manager remove uname=jandoe
```

