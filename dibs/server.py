from   datetime import datetime, timedelta
from   decouple import config
import bottle
from   bottle import route, run, template, request
from   bottle import get, post, request, redirect, response
from   peewee import *
from   os import path

from .database import Item, Loan


# A note about using Peewee: Peewee queries are lazy-executed: they return
# iterators that must be accessed before the query is actually executed.
# Thus, when selecting items, the following returns a ModelSelector, and not
# a single result or a list of results:
#
#   Item.select().where(Item.barcode == barcode)
#
# and you can't do next(...) on this because it's an iterator and not a
# generator.  You have to either use a for loop, or create a list from the
# above before you can do much with it.


# Administrative interface endpoints.
# .............................................................................
# These endpoints need to be protected against access by non-Library staff.
# (Right now, there's no protection or distinction from other endpoints.)

@get('/list')
def list_items():
    return template(path.join(config('TEMPLATE_DIR'), 'list'),
                    items = Item.select(),
                    loans = Loan.select())


@get('/add')
def add():
    return template(path.join(config('TEMPLATE_DIR'), 'add'))


@post('/add')
def add_item():
    barcode  = request.POST.inputBarcode.strip()
    title    = request.POST.inputTitle.strip()
    author   = request.POST.inputAuthor.strip()
    copies   = request.POST.inputCopies.strip()
    tind_id  = request.POST.inputTindId.strip()
    duration = request.POST.inputDuration.strip()

    new_item = Item.create(barcode = barcode, title = title, author = author,
                           tind_id = tind_id, num_copies = copies,
                           duration = duration)

@post('/remove')
def remove_item():
    barcode = request.POST.barcode.strip()
    Item.delete().where(Item.barcode == barcode).execute()
    return template(path.join(config('TEMPLATE_DIR'), 'list'),
                    items = Item.select(),
                    loans = Loan.select())


# User endpoints.
# .............................................................................

@get('/item/<barcode:int>')
def show_item_info(barcode):
    remote_expired_sessions()
    user = 'someone@caltech.edu'
    loans = list(Loan.select(Loan, Item).join(Item).where(Loan.item.barcode == barcode))
    if any(loan.user for loan in loans if user == loan.user):
        # FIXME tell user they've already loaned one copy
        print(f'user already has a copy of {barcode} loaned out')
        return template(path.join(config('TEMPLATE_DIR'), 'item'),
                        item = Item.get(Item.barcode == barcode),
                        available = False)

    item = Item.get(Item.barcode == barcode)
    available = len(loans) < item.num_copies
    return template(path.join(config('TEMPLATE_DIR'), 'item'),
                    item = Item.get(Item.barcode == barcode),
                    available = available)


@post('/loan')
def loan_item():
    remote_expired_sessions()
    user = 'someone@caltech.edu'
    barcode = request.POST.inputBarcode.strip()

    loans = list(Loan.select(Loan, Item).join(Item).where(Loan.item.barcode == barcode))
    item = Item.get(Item.barcode == barcode)
    if len(loans) >= item.num_copies:
        # The item page should not make loans available to this user, but we
        # might reach this point some other way. FIXME tell user can't have loan.
        print(f'num loans: {len(loans)}')
        redirect(f'/item/{barcode}')
        return f'/item/{barcode}'

    if any(loan.user for loan in loans if user == loan.user):
        # FIXME tell user they've already loaned one copy.
        print(f'user already has a copy of {barcode} loaned out')
        return f'/item/{barcode}'

    item = Item.get(Item.barcode == barcode)
    loan = Loan.create(item = item.itemid,
                       started = datetime.now(),
                       endtime = datetime.now() + timedelta(hours = item.duration),
                       user = user)

    print('new loan created')
    return f'/view/{barcode}'


# The following method is meant to be called from APIs.

@get('/view/<barcode:int>')
def view_item(barcode):
    remote_expired_sessions()
    user = 'someone@caltech.edu'
    loans = Loan.select(Loan, Item).join(Item).where(Loan.item.barcode == barcode)
    if any(loan.user for loan in loans if user == loan.user):
        return f'Pretend this is the viewer page for {barcode}'


@get('/return/<barcode:int>')
def return_item(barcode):
    remote_expired_sessions()
    user = 'someone@caltech.edu'
    loans = Loan.select(Loan, Item).join(Item).where(Loan.item.barcode == barcode)
    user_loans = [loan for loan in loans if user == loan.user]
    if len(user_loans) > 1:
        # Internal error -- users should not have more than one loan of an item
        print(f'error: more than one loan by same user')
    elif user_loans:
        # User has a copy of this item loaned out. Delete the record.
        user_loans[0].delete_instance()
        print(f'deleted loan record for {barcode} by {user}')
    else:
        # User does not have this item loaned out. Ignore the request.
        print(f'user {user} does not have {barcode} loaned out')


# Server runner.
# .............................................................................

class Server():
    def __init__(self, host = 'localhost', port = 8080, debug = True):
        self.host = host
        self.port = port
        self.debug = debug


    def run(self):
        bottle.debug(self.debug)
        bottle.run(reloader = True, host = self.host, port = self.port)


# Utilitye functions.
# .............................................................................

def remote_expired_sessions():
    for loan in list(Loan.select()):
        if datetime.now() >= loan.endtime:
            print(f'deleting expired loan for {loan.user}')
            loan.delete_instance()
