'''
people.py provides authorization for a person based on their statues
in the person table.

It requires an SQLite3 database called people.db for managing user
information used to staff as well as last login time to expire
logins and force a re-authorization. In development the "secret" field
is used for authentication but in a production setting OAuth2+OpenID
is used to authentication and retrieving the userid.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from datetime import datetime

from hashlib import blake2b
from getpass import getpass

from decouple import config
from peewee import SqliteDatabase, Model
from peewee import AutoField, CharField, TimestampField

import os


def hashify(s):
    '''Return retring as blake2b has digest'''
    h = blake2b()
    h.update(str.encode(s))
    return h.hexdigest()

def update_password(secret):
    if not secret:
        secret = getpass(prompt='Password: ', stream = None)
    if not secret:
        return None
    else:
        return hashify(secret)

def check_password(src, secret):
    src = hashify(src)
    if src == secret:
        return True
    return False

# Figure out how are authentication and authorization is configured.
_db = SqliteDatabase(config('DATABASE_FILE', default='dibs.db'))


# Person is for development, it uses a SQLite3 DB to user
# connection validation data.
class Person(Model):
    uname = CharField()  # user name, e.g. janedoe
    secret = CharField() # password
    role = CharField()   # role is empty or "staff"
    display_name = CharField() # display_name, optional
    updated = TimestampField() # last successful login timestamp

    def has_role(self, required_role):
        return self.role == required_role

    class Meta:
        database = _db


# GuestPerson only exists while REMOTE_USER available in the environment.
# It is not stored in the person table as the Person model is.
class GuestPerson():
    '''GuestPerson is an object for non-staff people.  It has the same
    signature but is not persisted in the person table of the database.
    '''
    def __init__(self, uname = '', display_name = '', role = ''):
        self.uname = uname               # user name, e.g. janedoe
        self.display_name = display_name # display_name, optional
        self.role = role                 # role is empty or "staff"
        self.updated = datetime.now()

    def has_role(self, required_role):
        return self.role == required_role


def person_from_environ(environ):
    if 'REMOTE_USER' in environ:
        # NOTE: If we're shibbed then we always return a Person object.
        # Either they are a known person (e.g. library staff) or other community
        # member without a role.
        person = Person.get_or_none(Person.uname == environ['REMOTE_USER'])
        if person == None:
            person = GuestPerson()
            person.uname = environ['REMOTE_USER']
            person.display_name = environ['REMOTE_USER']
        return person
    else:
        return None
