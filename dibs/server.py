'''
server.py: server definition for DIBS

This uses Bottle (https://bottlepy.org/docs/stable/), a simple micro framework
for web services similar to Flask.
'''

from   contextlib import redirect_stderr
from   datetime import datetime, timedelta
from   decouple import config
import bottle
from   bottle import redirect, request, response, route, template, get, post
import logging
from   peewee import *
import os
from   os import path

if __debug__:
    from sidetrack import log

from .database import Item, Loan


# Constants used throughout this file.
# .............................................................................

_TEMPLATE_DIR = config('TEMPLATE_DIR')


# Administrative interface endpoints.
# .............................................................................
# These endpoints need to be protected against access by non-Library staff.
# (Right now, there's no protection or distinction from other endpoints.)

# A note about the way our POST actions work.  The POST actions are executed
# using a small bit of JavaScript in the associated HTML pages (see, e.g.,
# dibs/templates/item.tpl).  That JavaScript uses AJAX to send the POST
# request with form data.  Our POST route handlers below do whatever action
# is needed, and then return a string (not a page, not a template).  The AJAX
# handler in our web page expects this and sets the value of the web page's
# location.href to the string returned, thus moving the user to whatever page
# we want to be shown after the action is done.

# A note about using Peewee: Peewee queries are lazy-executed: they return
# iterators that must be accessed before the query is actually executed.
# Thus, when selecting items, the following returns a ModelSelector, and not
# a single result or a list of results:
#
#   Item.select().where(Item.barcode == barcode)
#
# and you can't do next(...) on this because it's an iterator and not a
# generator.  You have to either use a for loop, or create a list from the
# above before you can do much with it.  Creating lists in these cases would
# be inefficient, but we have so few items to deal with that it's not a
# concern currently.

@get('/list')
def list_items():
    '''Display the list of available items.'''
    if __debug__: log('get /list invoked')
    remove_expired_loans()
    return template(path.join(_TEMPLATE_DIR, 'list'),
                    items = Item.select(), loans = Loan.select())


@get('/add')
def add():
    '''Display the page to add new items.'''
    if __debug__: log('get /add invoked')
    return template(path.join(_TEMPLATE_DIR, 'add'))


@post('/add')
def add_item():
    '''Handle http post request to add a new item from the add-new-item page.'''
    if __debug__: log('post /add invoked')
    barcode  = request.POST.inputBarcode.strip()
    title    = request.POST.inputTitle.strip()
    author   = request.POST.inputAuthor.strip()
    copies   = request.POST.inputCopies.strip()
    tind_id  = request.POST.inputTindId.strip()
    duration = request.POST.inputDuration.strip()

    remove_expired_loans()
    if __debug__: log(f'creating new item for barcode {barcode}, title {title}')
    new_item = Item.create(barcode = barcode, title = title, author = author,
                           tind_id = tind_id, num_copies = copies,
                           duration = duration)
    return '/list'


@post('/remove')
def remove_item():
    '''Handle http post request to remove an item from the list page.'''
    barcode = request.POST.barcode.strip()
    if __debug__: log(f'post /remove invoked on barcode {barcode}')

    remove_expired_loans()
    # Guard against trying to delete a nonexistent item.
    try:
        item = Item.get(Item.barcode == barcode)
        # Don't forget to delete any loans involving this item.
        if list(Loan.select(Loan.item == item)):
            Loan.delete().where(Loan.item == item).execute()
        Item.delete().where(Item.barcode == barcode).execute()
    except DoesNotExist as ex:
        if __debug__: log(f'there is no item with barcode {barcode}')
    return template(path.join(_TEMPLATE_DIR, 'list'),
                    items = Item.select(), loans = Loan.select())


# User endpoints.
# .............................................................................

@get('/item/<barcode:int>')
def show_item_info(barcode):
    '''Display information about the given item.'''
    user = 'someone@caltech.edu'
    if __debug__: log(f'get /item invoked on barcode {barcode} by user {user}')

    remove_expired_loans()
    try:
        item = Item.get(Item.barcode == barcode)
        loans = list(Loan.select().where(Loan.item == item))
        if any(loan.user for loan in loans if user == loan.user):
            # FIXME tell user they've already loaned one copy
            if __debug__: log(f'user already has a copy of {barcode} loaned out')
            return template(path.join(_TEMPLATE_DIR, 'item'), item = item,
                            available = False)
        available = len(loans) < item.num_copies
        return template(path.join(_TEMPLATE_DIR, 'item'), item = item,
                        available = available)
    except DoesNotExist as ex:
        if __debug__: log(f'there is no item with barcode {barcode}')
        return template(path.join(_TEMPLATE_DIR, 'nonexistent'), barcode = barcode)


@post('/loan')
def loan_item():
    '''Handle http post request to loan out an item, from the item info page.'''
    user = 'someone@caltech.edu'
    barcode = request.POST.inputBarcode.strip()
    if __debug__: log(f'post /loan invoked on barcode {barcode} by user {user}')

    remove_expired_loans()
    try:
        item = Item.get(Item.barcode == barcode)
        loans = list(Loan.select().where(Loan.item == item))
        if len(loans) >= item.num_copies:
            # The item page shouldn't make loans available to this user, but we
            # might reach this point some other way. FIXME tell user can't loan.
            if __debug__: log(f'# loans {len(loans)} >= num_copies for {barcode} ')
            return f'/item/{barcode}'
        if any(loan.user for loan in loans if user == loan.user):
            # FIXME tell user they've already loaned one copy.
            if __debug__: log(f'user already has a copy of {barcode} loaned out')
            return f'/item/{barcode}'

        # The user is allowed to loan out this item.
        Loan.create(item = item.itemid,
                    user = user,
                    started = datetime.now(),
                    endtime = datetime.now() + timedelta(hours = item.duration))
        if __debug__: log(f'new loan created for {barcode} for {user}')
        return f'/view/{barcode}'
    except DoesNotExist as ex:
        if __debug__: log(f'there is no item with barcode {barcode}')
        return template(path.join(_TEMPLATE_DIR, 'nonexistent'), barcode = barcode)


@get('/view/<barcode:int>')
def send_item_to_viewer(barcode):
    '''Redirect to the viewer.'''
    user = 'someone@caltech.edu'
    if __debug__: log(f'get /view invoked on barcode {barcode} by user {user}')

    remove_expired_loans()
    try:
        item = Item.get(Item.barcode == barcode)
        loans = list(Loan.select().where(Loan.item == item))
        if any(loan.user for loan in loans if user == loan.user):
            if __debug__: log(f'returning loan URL for {barcode} for {user}')
            return f'Pretend this is the viewer page for {barcode}'
        else:
            if __debug__: log(f'user {user} does not have {barcode} loaned out')
            return template(path.join(_TEMPLATE_DIR, 'notallowed'),
                            item = Item.get(Item.barcode == barcode))
    except DoesNotExist as ex:
        if __debug__: log(f'there is no item with barcode {barcode}')
        return template(path.join(_TEMPLATE_DIR, 'nonexistent'), barcode = barcode)


@get('/return/<barcode:int>')
def return_item(barcode):
    '''Handle http get request to return the given item early.'''
    user = 'someone@caltech.edu'
    if __debug__: log(f'get /return invoked on barcode {barcode} by user {user}')

    remove_expired_loans()
    try:
        item = Item.get(Item.barcode == barcode)
        loans = list(Loan.select().where(Loan.item == item))
        user_loans = [loan for loan in loans if user == loan.user]
        if len(user_loans) > 1:
            # Internal error -- users should not have more than one loan of an
            # item. Right now, we simply log it and move on.
            if __debug__: log(f'error: more than one loan for {barcode} by {user}')
        elif user_loans:
            # Normal case: user has loaned a copy of item. Delete the record.
            if __debug__: log(f'deleting loan record for {barcode} by {user}')
            user_loans[0].delete_instance()
        else:
            # User does not have this item loaned out. Ignore the request.
            if __debug__: log(f'user {user} does not have {barcode} loaned out')
    except DoesNotExist as ex:
        if __debug__: log(f'there is no item with barcode {barcode}')
        return template(path.join(_TEMPLATE_DIR, 'nonexistent'), barcode = barcode)


# Server runner.
# .............................................................................

class Server():
    def __init__(self, host = 'localhost', port = 8080,
                 debug = False, reload = True):
        if __debug__ and not ('BOTTLE_CHILD' in os.environ):
            log(f'initializing Server object')
        self.host = host
        self.port = port
        self.debug = debug
        self.reload = reload


    def run(self):
        child = ('BOTTLE_CHILD' in os.environ)
        if __debug__: log(f'running {"child " if child else ""}server process')
        if self.debug:
            sidetrack_logger = logging.getLogger('sidetrack')
            sidetrack_stream = sidetrack_logger.handlers[0].stream
            with redirect_stderr(sidetrack_stream):
                bottle.debug(True)
                bottle.run(host = self.host, port = self.port, reloader = self.reload)
        else:
            bottle.run(host = self.host, port = self.port, reloader = self.reload)


# Utilitye functions.
# .............................................................................

def remove_expired_loans():
    for loan in list(Loan.select()):
        if datetime.now() >= loan.endtime:
            print(f'deleting expired loan for {loan.user}')
            loan.delete_instance()
