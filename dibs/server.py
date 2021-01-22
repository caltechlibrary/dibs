'''
server.py: server definition for DIBS

This uses Bottle (https://bottlepy.org/docs/stable/), a simple micro framework
for web services similar to Flask.
'''

from   contextlib import redirect_stderr
from   datetime import datetime, timedelta
from   decouple import config
import bottle
from   bottle import Bottle, HTTPResponse, static_file, template
from   bottle import request, response, redirect, route, get, post, error
from   bottle_session import SessionPlugin
import logging
from   peewee import *
import os
from   os import path
import smtplib
import threading

if __debug__:
    from sidetrack import log

from .database import Item, Loan, Recent


# Installation of Bottle plugins.
# .............................................................................

bottle.install(SessionPlugin(cookie_name = config('COOKIE_NAME'),
                             cookie_lifetime = config('COOKIE_LIFETIME')))


# Constants used throughout this file.
# .............................................................................

# Where our Bottle templates are stored.
_TEMPLATE_DIR = config('TEMPLATE_DIR')

# Lock object used around some code to prevent concurrent modification.
_THREAD_LOCK = threading.Lock()

# Body of email message sent to users
_EMAIL = '''From: {sender}
To: {user}
Subject: {subject}

You started a digital loan through Caltech DIBS at {start}.

  Title: {item.title}
  Author: {item.author}

  The loan period ends at {end}
  Web viewer: {viewer}

Information about loan policies can be found at {info_page}

Thank you for using Caltech DIBS. We hope the experience is a pleasant one.
Please don't hesitate to send us feedback using our anonymous feedback form
at {feedback}
'''


# Decorators used throughout this file.
# .............................................................................

def expired_loans_removed(func):
    '''Clean up expired loans before the function is called.'''
    # FIXME: Checking the loans at every function call is not efficient.  This
    # approach needs to be replaced with some more efficient.
    def wrapper(session, *args, **kwargs):
        for loan in Loan.select():
            if datetime.now() >= loan.endtime:
                barcode = loan.item.barcode
                if __debug__: log(f'creating recent record for {barcode} by {loan.user}')
                Recent.create(item = loan.item, user = loan.user,
                              nexttime = loan.endtime + timedelta(hours = 1))
                if __debug__: log(f'expiring loan of {barcode} by {loan.user}')
                loan.delete_instance()
        for recent in Recent.select():
            if datetime.now() >= recent.nexttime:
                barcode = recent.item.barcode
                if __debug__: log(f'expiring recent record for {barcode} by {recent.user}')
                recent.delete_instance()
        return func(session, *args, **kwargs)
    return wrapper


def barcode_verified(func):
    '''Check if the given barcode (passed as keyword argument) exists.'''
    def wrapper(session, *args, **kwargs):
        if 'barcode' in kwargs:
            barcode = kwargs['barcode']
            try:
                Item.get(Item.barcode == barcode)
            except DoesNotExist as ex:
                if __debug__: log(f'there is no item with barcode {barcode}')
                return template(path.join(_TEMPLATE_DIR, 'nonexistent'),
                                barcode = barcode)
        return func(session, *args, **kwargs)
    return wrapper


def authenticated(func):
    def wrapper(session, *args, **kwargs):
        if 'user' not in session or session['user'] is None:
            redirect('/notauthenticated')
        else:
            if __debug__: log(f'user is authenticated: {session["user"]}')
        return func(session, *args, **kwargs)
    return wrapper


# Administrative interface endpoints.
# .............................................................................
# These endpoints need to be protected against access by non-Library staff.
# (Right now, there's no protection or distinction from other endpoints.)

@get('/')
def list_items(session):
    '''Display the welcome page.'''
    if __debug__: log('get / invoked')
    return template(path.join(_TEMPLATE_DIR, 'welcome'))


@get('/login')
def show_login_page(session):
    if __debug__: log('get /login invoked')
    return template(path.join(_TEMPLATE_DIR, 'login'))


@post('/login')
def login(session):
    email = request.forms.get('email')
    password = request.forms.get('password')
    if __debug__: log(f'post /login invoked by {email}')
    if password != config('DEMO_PASSWORD'):
        if __debug__: log(f'wrong password -- rejecting {email}')
        return template(path.join(_TEMPLATE_DIR, 'login'))
    else:
        if __debug__: log(f'creating session for {email}')
        session['user'] = email
        redirect('/')


@get('/logout')
def logout(session):
    if 'user' not in session:
        if __debug__: log(f'get /logout invoked by unauthenticated user')
        redirect('/login')
    else:
        user = session['user']
        if __debug__: log(f'get /logout invoked by {user}')
        del session['user']
        redirect('/login')


@get('/list')
@expired_loans_removed
@authenticated
def list_items(session):
    '''Display the list of known items.'''
    if __debug__: log('get /list invoked')
    return template(path.join(_TEMPLATE_DIR, 'list'),
                    items = Item.select(), loans = Loan.select())


@get('/add')
@authenticated
def add(session):
    '''Display the page to add new items.'''
    if __debug__: log('get /add invoked')
    return template(path.join(_TEMPLATE_DIR, 'add'))


@post('/add')
@authenticated
def add_item(session):
    '''Handle http post request to add a new item from the add-new-item page.'''
    if __debug__: log('post /add invoked')
    barcode  = request.POST.inputBarcode.strip()
    title    = request.POST.inputTitle.strip()
    author   = request.POST.inputAuthor.strip()
    copies   = request.POST.inputCopies.strip()
    tind_id  = request.POST.inputTindId.strip()
    duration = request.POST.inputDuration.strip()

    if __debug__: log(f'creating new item for barcode {barcode}, title {title}')
    Item.create(barcode = barcode, title = title, author = author,
                tind_id = tind_id, num_copies = copies, duration = duration)
    redirect('/list')


@post('/ready')
@expired_loans_removed
@barcode_verified
@authenticated
def toggle_ready(session):
    '''Set the ready-to-loan field.'''
    barcode = request.POST.barcode.strip()
    ready = (request.POST.ready.strip() == 'True')
    if __debug__: log(f'post /ready invoked on barcode {barcode}')
    item = Item.get(Item.barcode == barcode)
    # The status we get is the availability status as it currently shown,
    # meaning the user's action is to change the status.
    item.ready = not ready
    item.save()
    if __debug__: log(f'readiness of {barcode} is now {item.ready}')
    # If the readiness state is changed after the item is let out for loans,
    # then there may be outstanding loans right now. Delete them.
    if list(Loan.select(Loan.item == item)):
        if __debug__: log(f'loans for {barcode} have been deleted')
        Loan.delete().where(Loan.item == item).execute()
    redirect('/list')


@post('/remove')
@expired_loans_removed
@barcode_verified
@authenticated
def remove_item(session):
    '''Handle http post request to remove an item from the list page.'''
    barcode = request.POST.barcode.strip()
    if __debug__: log(f'post /remove invoked on barcode {barcode}')

    item = Item.get(Item.barcode == barcode)
    item.ready = False
    # Don't forget to delete any loans involving this item.
    if list(Loan.select(Loan.item == item)):
        Loan.delete().where(Loan.item == item).execute()
    Item.delete().where(Item.barcode == barcode).execute()
    redirect('/list')


# User endpoints.
# .............................................................................

@get('/item/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
def show_item_info(session, barcode):
    '''Display information about the given item.'''
    user = session.get('user')
    if __debug__: log(f'get /item invoked on barcode {barcode} by user {user}')

    item = Item.get(Item.barcode == barcode)
    user_loans = list(Loan.select().where(Loan.user == user))
    recent_history = list(Recent.select().where(Recent.item == item))
    # First check if the user has recently loaned out this same item.
    if any(loan for loan in recent_history if loan.user == user):
        if __debug__: log(f'user recently borrowed {barcode}')
        recent = next(loan for loan in recent_history if loan.user == user)
        endtime = recent.nexttime
        available = False
    elif any(user_loans):
        # The user has a current loan. If it's for this title, redirect them
        # to the viewer; if it's for another title, block the loan button.
        if user_loans[0].item == item:
            if __debug__: log(f'user already has {barcode}; redirecting to uv')
            redirect(f'/view/{barcode}')
            return
        else:
            if __debug__: log(f'user already has a loan on something else')
            available = False
            endtime = user_loans[0].endtime
    else:
        if __debug__: log(f'user is allowed to borrow {barcode}')
        loans = list(Loan.select().where(Loan.item == item))
        available = item.ready and (len(loans) < item.num_copies)
        if item.ready and loans:
            endtime = min(loan.endtime for loan in loans)
        elif item.ready:
            endtime = datetime.now()
        else:
            endtime = None
    return template(path.join(_TEMPLATE_DIR, 'item'),
                    item = item, available = available, endtime = endtime)


@post('/loan')
@expired_loans_removed
@barcode_verified
@authenticated
def loan_item(session):
    '''Handle http post request to loan out an item, from the item info page.'''
    user = session.get('user')
    barcode = request.POST.barcode.strip()
    if __debug__: log(f'post /loan invoked on barcode {barcode} by user {user}')

    item = Item.get(Item.barcode == barcode)
    if not item.ready:
        # Normally we shouldn't see a loan request through our form in this
        # case, so either staff has changed the status after item was made
        # available or someone got here accidentally (or deliberately).
        if __debug__: log(f'{barcode} is not ready for loans')
        redirect(f'/view/{barcode}')
        return

    # The default Bottle dev web server is single-thread, so we won't run into
    # the problem of 2 users simultaneously clicking on the loan button.  Other
    # servers are multithreaded, and there's a risk that the time it takes us
    # to look through the loans introduces a window of time when another user
    # might click on the same loan button and cause another loan request to be
    # initiated before the 1st finishes.  So, lock this block of code.
    with _THREAD_LOCK:
        if any(Loan.select().where(Loan.user == user)):
            if __debug__: log(f'user already has a loan on something else')
            redirect(f'/onlyone')
            return
        loans = list(Loan.select().where(Loan.item == item))
        if any(loan.user for loan in loans if user == loan.user):
            # Shouldn't be able to reach this point b/c the item page shouldn't
            # make a loan available for this user & item combo. But if
            # something weird happens (e.g., double posting), we might.
            if __debug__: log(f'user already has a copy of {barcode} loaned out')
            if __debug__: log(f'redirecting user to /view for {barcode}')
            redirect(f'/view/{barcode}')
            return
        if len(loans) >= item.num_copies:
            # This shouldn't be possible, but catch it anyway.
            if __debug__: log(f'# loans {len(loans)} >= num_copies for {barcode} ')
            redirect(f'/item/{barcode}')
            return
        recent_history = list(Recent.select().where(Recent.item == item))
        if any(loan for loan in recent_history if loan.user == user):
            if __debug__: log(f'user recently borrowed {barcode}')
            recent = next(loan for loan in recent_history if loan.user == user)
            return template(path.join(_TEMPLATE_DIR, 'toosoon'),
                            nexttime = recent.nexttime)
        # OK, the user is allowed to loan out this item.
        start = datetime.now()
        end   = start + timedelta(hours = item.duration)
        if __debug__: log(f'creating new loan for {barcode} for {user}')
        Loan.create(item = item, user = user, started = start, endtime = end)
        send_email(user, item, start, end)
    redirect(f'/view/{barcode}')


@get('/return/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
def end_loan(session, barcode):
    '''Handle http get request to return the given item early.'''
    user = session.get('user')
    if __debug__: log(f'get /return invoked on barcode {barcode} by user {user}')

    loans = list(Loan.select().join(Item).where(Loan.item.barcode == barcode))
    user_loans = [loan for loan in loans if user == loan.user]
    if len(user_loans) > 1:
        # Internal error -- users should not have more than one loan of an
        # item. Right now, we simply log it and move on.
        if __debug__: log(f'error: more than one loan for {barcode} by {user}')
    elif user_loans:
        # Normal case: user has loaned a copy of item. Delete the record and
        # add a new Recent loan record.
        if __debug__: log(f'deleting loan record for {barcode} by {user}')
        user_loans[0].delete_instance()
        Recent.create(item = Item.get(Item.barcode == barcode),
                      user = user,
                      nexttime = datetime.now() + timedelta(hours = 1))
    else:
        # User does not have this item loaned out. Ignore the request.
        if __debug__: log(f'user {user} does not have {barcode} loaned out')
    redirect('/thankyou')


@get('/view/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
def send_item_to_viewer(session, barcode):
    '''Redirect to the viewer.'''
    user = session.get('user')
    if __debug__: log(f'get /view invoked on barcode {barcode} by user {user}')

    loans = list(Loan.select().join(Item).where(Loan.item.barcode == barcode))
    user_loans = [loan for loan in loans if user == loan.user]
    if user_loans:
        if __debug__: log(f'redirecting to viewer for {barcode} for {user}')
        return template(path.join(_TEMPLATE_DIR, 'uv'), barcode = barcode,
                        endtime = user_loans[0].endtime)
    else:
        if __debug__: log(f'user {user} does not have {barcode} loaned out')
        return template(path.join(_TEMPLATE_DIR, 'notallowed'))


@get('/manifests/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
def return_manifest(session, barcode):
    '''Return the manifest file for a given item.'''
    user = session.get('user')
    if __debug__: log(f'get /manifests/{barcode} invoked by user {user}')

    loans = list(Loan.select().join(Item).where(Loan.item.barcode == barcode))
    if any(loan.user for loan in loans if user == loan.user):
        if __debug__: log(f'returning manifest file for {barcode} for {user}')
        return static_file(f'{barcode}-manifest.json', root = 'manifests')
    else:
        if __debug__: log(f'user {user} does not have {barcode} loaned out')
        return template(path.join(_TEMPLATE_DIR, 'notallowed'))


@get('/thankyou')
def say_thank_you():
    return template(path.join(_TEMPLATE_DIR, 'thankyou'),
                    feedback_url = config('FEEDBACK_URL'))


@get('/info')
def say_thank_you():
    return template(path.join(_TEMPLATE_DIR, 'info'))


@get('/notauthenticated')
def say_thank_you():
    return template(path.join(_TEMPLATE_DIR, 'notauthenticated'))


# Universal viewer interface.
# .............................................................................
# The uv subdirectory contains generic html and css.  We serve them as static
# files to anyone; they don't need to be controlled.  The multiple routes
# are because the UV files themselves reference different paths.

@route('/view/uv/<filepath:path>')
@route('/viewer/uv/<filepath:path>')
def serve_uv_files(filepath):
    if __debug__: log(f'serving static uv file /viewer/uv/{filepath}')
    return static_file(filepath, root = 'viewer/uv')


# The uv subdirectory contains generic html and css. Serve as static files.
@route('/viewer/<filepath:path>')
def serve_uv_files(filepath):
    if __debug__: log(f'serving static uv file /viewer/{filepath}')
    return static_file(filepath, root = 'viewer')


# Error pages.
# .............................................................................

@get('/nonexistent')
@get('/nonexistent/<barcode:int>')
def nonexistent_item(barcode = None):
    '''Serve as an endpoint for telling users about nonexistent items.'''
    if __debug__: log(f'nonexistent_item called with {barcode}')
    return template(path.join(_TEMPLATE_DIR, 'nonexistent'), barcode = barcode)


@error(404)
def error404(error):
    if __debug__: log(f'error404 called with {error}')
    return template(path.join(_TEMPLATE_DIR, 'error'),
                    code = error.status_code, message = error.body)


@error(405)
def error405(error):
    if __debug__: log(f'error405 called with {error}')
    return template(path.join(_TEMPLATE_DIR, 'notallowed'))


# Server runner.
# .............................................................................

class Server():
    def __init__(self, host = 'localhost', port = 8080,
                 debug = False, reload = True):
        if __debug__ and not ('BOTTLE_CHILD' in os.environ):
            log(f'initializing Server object')
        self.host = host
        self.port = int(port)
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


# Miscellaneous utilities.
# .............................................................................

def send_email(user, item, start, end):
   try:
       subject = f'Caltech DIBS loan for "{item.title}"'
       dibs_host = config('DIBS_HOST')
       dibs_port = config('DIBS_PORT')
       viewer = f'https://{dibs_host}:{dibs_port}/view/{item.barcode}'
       info_page = f'https://{dibs_host}:{dibs_port}/info'
       body = _EMAIL.format(item      = item,
                            start     = start.strftime("%I:%M %p %Z on %A, %B %d"),
                            end       = end.strftime("%I:%M %p %Z on %A, %B %d"),
                            viewer    = viewer,
                            info_page = info_page,
                            user      = user,
                            subject   = subject,
                            sender    = config('MAIL_SENDER'),
                            host      = dibs_host,
                            port      = dibs_port,
                            feedback  = config('FEEDBACK_URL'))
       if __debug__: log(f'sending mail to {user} about loan of {item.barcode}')
       mailer  = smtplib.SMTP(config('MAIL_HOST'))
       mailer.sendmail(config('MAIL_SENDER'), [user], body)
   except Exception as ex:
       if __debug__: log(f'unable to send mail: {str(ex)}')
