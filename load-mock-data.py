from decouple import config
from peewee import SqliteDatabase

from cdl.database import Item

db = SqliteDatabase(config('DATABASE_FILE'))

# Peewee autoconnects to the database if doing queries but not other ops.
db.connect()
db.create_tables([Item])

# Random books found in TIND.
Item.create(barcode    = '35047019626837',
            title      = 'Fundamentals of geophysics',
            author     = 'Lowrie',
            tind_id    = 990468,
            num_copies = 1
)

Item.create(barcode    = '35047019626829',
            title      = 'GIS for science',
            author     = 'Wright',
            tind_id    = 990456,
            num_copies = 1
)

Item.create(barcode    = '350470000611207',
            title      = 'Pack my bag',
            author     = 'Green',
            tind_id    = 466498,
            num_copies = 1
)
