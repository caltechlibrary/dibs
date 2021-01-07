'''
schema.py: object definitions for the database
'''

from decouple import config
from peewee import SqliteDatabase, Model
from peewee import CharField, TextField, IntegerField, SmallIntegerField


# Database object schemas
# .............................................................................

_db = SqliteDatabase(config('DATABASE_FILE'))

class BaseModel(Model):
    class Meta:
        database = _db


class Item(BaseModel):
    barcode    = CharField(unique = True)
    title      = TextField()
    author     = TextField()
    tind_id    = IntegerField()
    num_copies = SmallIntegerField()
