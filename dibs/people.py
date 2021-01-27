'''
auth.py provides a means of managing authentication and authorization.
It requires an SQLite3 database called people.db for managing user
information used to staff as well as last login time to expire
logins and force a re-authorization. In development the "secret" field
is used for authentication but in a production setting OAuth2+OpenID
is used to authentication and retrieving the userid.
'''

from hashlib import blake2b
from getpass import getpass

from decouple import config
from peewee import SqliteDatabase, Model
from peewee import AutoField, CharField, TimestampField

def hashify(s):
    '''Return retring as blake2b has digest'''
    h = blake2b()
    h.update(str.encode(s))
    return h.hexdigest()

def update_password(secret):
    if not secret:
        secret = getpass(prompt='Password: ', stream = None)
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
    auth_type = CharField() # local, OAuth2
    updated = TimestampField() # last successful login timestamp

    class Meta:
        database = _db


