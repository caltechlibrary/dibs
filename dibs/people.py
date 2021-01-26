'''
auth.py provides a means of managing authentication and authorization.
It requires an SQLite3 database called people.db for managing user
information used to staff as well as last login time to expire
logins and force a re-authorization. In development the "secret" field
is used for authentication but in a production setting OAuth2+OpenID
is used to authentication and retrieving the userid.
'''

from decouple import config
from peewee import SqliteDatabase, Model
from peewee import AutoField, CharField, TimestampField

# Figure out how are authentication and authorization is configured.
_people_db = config('PEOPLE_DB', default='people.db')
_auth_type = config('AUTH_TYPE', default='local')

# People is for development, it uses a SQLite3 DB to user
# connection validation data.
class People(Model):
    row_id = AutoField() # row ID
    uname = CharField()  # user name, e.g. janedoe
    role = CharField()   # role is empty or "staff"
    secret = CharField() # password
    display_name = CharField() # display_name, optional
    auth_time = TimestampField() # last successful login timestamp
    auth_type = CharField() # local, OAuth2

    class Meta:
        database = _people_db


