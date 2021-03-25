'''
database.py: object definitions for the database

This uses Peewee (http://docs.peewee-orm.com/en/latest/), a small ORM that
allows writing database code entirely in terms of Python objects without
having to know much about SQL.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from decouple import config
from peewee import SqliteDatabase, Model
from peewee import CharField, TextField, IntegerField, SmallIntegerField
from peewee import ForeignKeyField, AutoField, DateTimeField, BooleanField


# Database connection.
# .............................................................................
# Note: this is exported too, because other code sometimes needs to use context
# managers on the database object to perform some atomic operations.

database = SqliteDatabase(config('DATABASE_FILE', default='dibs.db'))


# Database object schemas.
# .............................................................................

class BaseModel(Model):
    '''Base PeeWee object model for all DIBS database objects.'''

    class Meta:
        database = database


class Item(BaseModel):
    '''An item available for borrowing through DIBS.

    Each item available for loaning out gets a separate Item object in the
    database.  We may allow more than one simultaneous loan of a given item,
    so that's why there's a num_copies field to represent how many copies of
    the thing we're allowed to loan.  The duration is set per-item because we
    could very well allow some items to be loaned out for longer periods than
    others.  Duration is in terms of hours right now.

    The fields for author, title, year, edition, and thumbnail are not
    strictly necessary for loan purposes. They are here to cache the values
    so that they don't have to be looked up when generating the /item page.
    FIXME: keeping this data introduces an opportunity for inconsistencies,
    if the source data (currently in TIND) gets changed.
    '''

    itemid     = AutoField()            # Auto-increment primary key.
    barcode    = CharField(unique = True)
    tind_id    = CharField()
    title      = TextField()
    author     = TextField()
    year       = CharField()
    edition    = CharField()
    thumbnail  = TextField()            # URL to an image.
    num_copies = SmallIntegerField()
    duration   = SmallIntegerField()    # Assumed to be hours.
    ready      = BooleanField(default = False)


class Loan(BaseModel):
    '''A current or recent loan in DIBS.

    Loans are currently stored in terms of a combination of item + user
    identity.  A user can have multiple items out; they just get represented
    as separate Loan object instances. Similarly, an Item can be loaned to
    multiple people, if there are multiple copies of the item.

    Loans periods could be represented as start + duration, but since we'll
    need to test against the end of a loan repeatedly, it's easier to store
    the end time here (in field end_time).

    Our policy is that users can't immediately check out the same item; they
    must instead wait a certain amount of time.  After a loan ends, the Loan
    object is not immediately deleted; instead, its state is changed, and the
    field "reloan_time" is given a value corresponding to the first moment
    when the user can borrow that item again.  Once the reloan time is
    passed, DIBS deletes the Loan object entirely.

    All time values are datetime objects in UTC.
    '''

    # Important: Peewee's DateTimeField is *not* time zone aware. If you hand
    # it a Python datetime value without a time zone, it will treat it as a
    # datetime object, but if you add a zone (e.g., storing a value like
    # datetime.now(tz = tz.tzlocal()) you will get string values. So, we store
    # all values as UTC and then convert to/from local time zone as needed.

    loanid      = AutoField()
    item        = ForeignKeyField(Item, column_name = 'itemid', backref = 'loanref')
    state       = CharField()           # String, either 'active' or 'recent'
    user        = TextField()           # Login, probably someone@caltech.edu
    start_time  = DateTimeField()       # When did the patron start the loan?
    end_time    = DateTimeField()       # When does the loan end?
    reloan_time = DateTimeField()       # When can this user loan this again?


# The History class is used to keep records of things for which we want to do
# basic statistics, such as which items are loaned out most.  It's a generic
# object class meant to be suitable for more than just loan data.  The
# intended use of the fields is as follows:
#
#  type:   what is the event? A short string like "loan".
#
#  what:   if the event involves an item, this string holds the item barcode,
#          else the string is a short description of the thing affected
#
#  start:  when did the even start
#
#  stop:   when did the event stop

class History(BaseModel):
    eventid    = AutoField()
    type       = CharField()            # String describing the event
    what       = CharField()            # What is this about? (e.g. a barcode)
    start_time = DateTimeField()        # When did the event start?
    end_time   = DateTimeField()        # When did the event stop?
