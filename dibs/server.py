'''
server.py: DIBS server definition.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   beaker.middleware import SessionMiddleware
import bottle
from   bottle import Bottle, HTTPResponse, static_file, template
from   bottle import request, response, redirect, route, get, post, error
from   commonpy.network_utils import net
from   datetime import datetime as dt
from   datetime import timedelta as delta
from   dateutil import tz
from   decouple import config
import functools
from   humanize import naturaldelta
import json
import os
from   os.path import realpath, dirname, join, exists
from   peewee import *
import random
import ratelimit
import string
import sys
from   tempfile import NamedTemporaryFile
from   topi import Tind

from .database import Item, Loan, Recent, database
from .date_utils import human_datetime
from .email import send_email
from .people import Person, check_password, person_from_session
from .roles import role_to_redirect, has_required_role

if __debug__:
    from sidetrack import log, logr, set_debug


# General configuration and initialization.
# .............................................................................

# Begin by creating a Bottle object on which we will define routes.  At the end
# of this file we will redefine this object by wrapping it with middleware, but
# first we will define routes and other behaviors on the basic Bottle instance.
dibs = Bottle()

# Tell Bottle where to find templates.  This is necessary for both the Bottle
# template() command to work and also to get %include to work inside our .tpl
# template files.  Rather surprisingly, the only way to tell Bottle where to
# find the templates is to set this Bottle package-level variable.
bottle.TEMPLATE_PATH.append(join(realpath(dirname(__file__)), 'templates'))

# Directory containing IIIF manifest files.
_MANIFEST_DIR = config('MANIFEST_DIR', default = 'manifests')

# The base URL of the IIIF server endpoint. Note: there is no reasonable
# default value for this one, so we fail if this is not set.
_IIIF_BASE_URL = config('IIIF_BASE_URL')

# Cooling-off period after a loan ends, before user can borrow same title again.
_RELOAN_WAIT_TIME = delta(minutes = int(config('RELOAN_WAIT_TIME', default = 30)))

# Where we send users to give feedback.
_FEEDBACK_URL = config('FEEDBACK_URL', default = '/')

# How many times a user can retry a login within a given window of time (sec).
_LOGIN_RETRY_TIMES = 5
_LOGIN_RETRY_WINDOW = 30

# The next constant is used to configure Beaker sessions. This is used at
# the very end of this file in the call to SessionMiddleware.
_SESSION_CONFIG = {
    # Save session data automatically, without requiring us to call save().
    'session.auto'    : True,

    # Session cookies should be accessible only to the browser, not JavaScript.
    'session.httponly': True,

    # Session cookies should be marked secure, but it requires https, so we
    # can't set it unconditionally.  Since this module (server.py) is loaded
    # before adapter.wsgi, we don't have the info about whether https is in
    # use.  Right now I don't see a better way but to use a settings.ini var.
    'session.secure'  : config('SECURE_COOKIES', default = False),

    # FIXME this is temporary and insecure.  When we have SSO hooked in,
    # session tracking needs to be revisited anyway.
    'session.type'    : 'file',
    'session.data_dir': config('SESSION_DIR', default = '/tmp/dibs'),
    'session.secret'  : config('SESSION_SECRET', default =
                               ''.join(random.choices(string.printable, k = 128))),

    # The name of the session cookie.
    'session.key'     : 'dibssession',

    # Seconds until the session is invalidated.
    'session.timeout' : config('SESSION_TIMEOUT', cast = int, default = 604800),
}


# General-purpose utilities used later.
# .............................................................................

def page(name, **kargs):
    '''Create a page using template "name" with some standard variables set.'''
    # Bottle is unusual in providing global objects like 'request'.
    session = request.environ.get('beaker.session', None)
    logged_in = session and bool(session.get('user', None))
    staff_user = logged_in and has_required_role(person_from_session(session), 'library')
    return template(name, base_url = dibs.base_url, logged_in = logged_in,
                    staff_user = staff_user, feedback_url = _FEEDBACK_URL, **kargs)


def debug_mode():
    '''Return True if we're running Bottle's default server in debug mode.'''
    return os.environ.get('BOTTLE_CHILD')


# Decorators -- functions that are run selectively on certain routes.
# .............................................................................

# Expiring loans this way is inefficient, but that's mitigated by the fact
# that we won't have a lot of loans at any given time.  This approach does
# have an advantage of simplicity in a multi-process Apache server config.
# The alternative would be to implement a separate reaper process of some
# kind, complicating things significantly.  (If we only had to worry about
# multiple threads, it would be easier, but our httpd runs processes.)

def expired_loans_removed(func):
    '''Clean up expired loans.'''
    @functools.wraps(func)
    def expired_loan_removing_wrapper(*args, **kwargs):
        now = dt.utcnow()
        for loan in Loan.select().where(now >= Loan.endtime):
            if __debug__: log(f'locking database')
            with database.atomic('immediate'):
                barcode = loan.item.barcode
                if __debug__: log(f'loan for {barcode} by {loan.user} expired')
                Recent.create(item = loan.item, user = loan.user,
                              nexttime = loan.endtime + delta(minutes = 1))
                loan.delete_instance()
        # Deleting outdated Recent records is a simpler procedure.
        num = Recent.delete().where(now >= Recent.nexttime).execute()
        if __debug__ and num: log(f'removed {num} outdated Recent records')
        return func(*args, **kwargs)
    return expired_loan_removing_wrapper


def barcode_verified(func):
    '''Check if the given barcode (passed as keyword argument) exists.'''
    @functools.wraps(func)
    def barcode_verification_wrapper(*args, **kwargs):
        # We always call the barcode variable "barcode" in our forms and pages
        # so it's possible to use this annotation on any route if needed.  This
        # function handles both GET & POST requests.  In the case of HTTP GET,
        # there will be an argument to the function called "barcode"; in the
        # case of HTTP POST, there will be a form variable called "barcode".
        barcode = None
        if 'barcode' in kwargs:
            barcode = kwargs['barcode']
        elif 'barcode' in request.POST:
            barcode = request.POST.barcode.strip()
        if __debug__ and barcode: log(f'verifying barcode {barcode}')
        if barcode and not Item.get_or_none(Item.barcode == barcode):
            if __debug__: log(f'there is no item with barcode {barcode}')
            return page('error', summary = 'no such barcode',
                        message = f'There is no item with barcode {barcode}.')
        return func(*args, **kwargs)
    return barcode_verification_wrapper


def authenticated(func):
    '''Check if the user is authenticated and redirect to /login if not.'''
    @functools.wraps(func)
    def authentication_check_wrapper(*args, **kwargs):
        if request.method == 'HEAD':
            # A Beaker session is not present when we get a HEAD.  Unsure if
            # that's expected or just a Bottle or Beaker behavior.  We can't
            # proceed with the request, but it's not an error either.  I
            # haven't found a better alternative than simply returning nothing.
            if __debug__: log(f'returning empty HEAD on {request.path}')
            return
        session = request.environ['beaker.session']
        if not session.get('user', None):
            if __debug__: log(f'user not found in session object')
            redirect(f'{dibs.base_url}/login')
        else:
            if __debug__: log(f'user is authenticated: {session["user"]}')
        return func(*args, **kwargs)
    return authentication_check_wrapper


def limit_login_attempts(func):
    '''Rate-limit the number of login attempts within a given period of time.'''
    @functools.wraps(func)
    def limit_login_attempts_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ratelimit.exception.RateLimitException as ex:
            client = request.environ.get('REMOTE_ADDR', 'unknown')
            if __debug__: log(f'rate limit exceeded for client {client}')
            return page('error', summary = 'too many login attempts',
                        message = f'Please try again later.')
    return limit_login_attempts_wrapper


# Administrative interface endpoints.
# .............................................................................

# NOTE: there are three approaches for integrating SSO. First is always
# require SSO before showing anything (not terribly useful here).
# Second use existing end points (e.g. /login, /logout) this supports
# everyone as SSO or not at all, third would be to support both
# SSO via its own end points and allow the app based authentication
# end points to remain for users who are defined in the system only.
# This can be helpful in the case of admin users or service accounts.

@dibs.get('/login')
def show_login_page():
    # NOTE: If SSO is implemented this should redirect to the
    # SSO end point with a return to /login on success.
    if __debug__: log('get /login invoked')
    return page('login')


@dibs.post('/login')
@limit_login_attempts
@ratelimit.limits(calls = _LOGIN_RETRY_TIMES, period = _LOGIN_RETRY_WINDOW)
def login():
    '''Handle performing the login action from the login page.'''
    # NOTE: If SSO is implemented this end point will handle the
    # successful login case applying role rules if necessary.
    email = request.forms.get('email').strip()
    password = request.forms.get('password')
    if __debug__: log(f'post /login invoked by {email}')
    # get our person obj from people.db for demo purposes
    user = Person.get_or_none(Person.uname == email)
    if not user:
        if __debug__: log(f'unknown user -- rejecting {email}')
        return page('login', login_failed = True)
    elif check_password(password, user.secret) == False:
        if __debug__: log(f'wrong password -- rejecting {email}')
        return page('login', login_failed = True)
    else:
        if __debug__: log(f'creating session for {email}')
        session = request.environ['beaker.session']
        session['user'] = email
        p = role_to_redirect(user.role)
        if __debug__: log(f'redirecting to "{p}"')
        redirect(f'{dibs.base_url}/{p}')


@dibs.post('/logout')
def logout():
    '''Handle the logout action from the navbar menu on every page.'''
    session = request.environ['beaker.session']
    if not session.get('user', None):
        if __debug__: log(f'post /logout invoked by unauthenticated user')
        return
    user = session['user']
    if __debug__: log(f'post /logout invoked by {user}')
    del session['user']
    redirect(f'{dibs.base_url}/login')


@dibs.get('/list')
@authenticated
def list_items():
    '''Display the list of known items.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        redirect(f'{dibs.base_url}/notallowed')
        return
    if __debug__: log('get /list invoked')
    return page('list', items = Item.select())


@dibs.get('/manage')
@authenticated
def list_items():
    '''Display the list of known items.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        redirect(f'{dibs.base_url}/notallowed')
        return
    if __debug__: log('get /manage invoked')
    return page('manage', items = Item.select())


@dibs.get('/add')
@authenticated
def add():
    '''Display the page to add new items.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        redirect(f'{dibs.base_url}/notallowed')
        return
    if __debug__: log('get /add invoked')
    return page('edit', action = 'add', item = None)


@dibs.get('/edit/<barcode:int>')
@barcode_verified
@authenticated
def edit(barcode):
    '''Display the page to add new items.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        redirect(f'{dibs.base_url}/notallowed')
        return
    if __debug__: log(f'get /edit invoked on {barcode}')
    return page('edit', action = 'edit', item = Item.get(Item.barcode == barcode))


@dibs.post('/update/add')
@dibs.post('/update/edit')
@expired_loans_removed
@authenticated
def update_item():
    '''Handle http post request to add a new item from the add-new-item page.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        redirect(f'{dibs.base_url}/notallowed')
        return
    if __debug__: log(f'post {request.path} invoked')
    if 'cancel' in request.POST:
        if __debug__: log(f'user clicked Cancel button')
        redirect(f'{dibs.base_url}/list')
        return

    # The HTML form validates the data types, but the POST might come from
    # elsewhere, so we always need to sanity-check the values.
    barcode = request.forms.get('barcode').strip()
    if not barcode.isdigit():
        return page('error', summary = 'invalid barcode',
                    message = f'{barcode} is not a valid barcode')
    duration = request.forms.get('duration').strip()
    if not duration.isdigit() or int(duration) <= 0:
        return page('error', summary = 'invalid duration',
                    message = f'Duration must be a positive number')
    num_copies = request.forms.get('num_copies').strip()
    if not num_copies.isdigit() or int(num_copies) <= 0:
        return page('error', summary = 'invalid copy number',
                    message = f'# of copies must be a positive number')

    item = Item.get_or_none(Item.barcode == barcode)
    if '/update/add' in request.path:
        if item:
            if __debug__: log(f'{barcode} already exists in the database')
            return page('error', summary = 'duplicate entry',
                        message = f'An item with barcode {barcode} already exists.')
        # Our current approach only uses items with barcodes that exist in
        # TIND.  If that ever changes, the following needs to change too.
        tind = Tind('https://caltech.tind.io')
        try:
            rec = tind.item(barcode = barcode).parent
        except:
            if __debug__: log(f'could not find {barcode} in TIND')
            return page('error', summary = 'no such barcode',
                        message = f'There is no item with barcode {barcode}.')
        if __debug__: log(f'locking database to add {barcode}, title {rec.title}')
        with database.atomic():
            Item.create(barcode = barcode, title = rec.title, author = rec.author,
                        tind_id = rec.tind_id, year = rec.year,
                        edition = rec.edition, thumbnail = rec.thumbnail_url,
                        num_copies = num_copies, duration = duration)
    else: # The operation is /update/edit.
        if not item:
            if __debug__: log(f'there is no item with barcode {barcode}')
            return page('error', summary = 'no such barcode',
                        message = f'There is no item with barcode {barcode}.')
        if __debug__: log(f'locking database to save changes to {barcode}')
        with database.atomic():
            item.barcode    = barcode
            item.duration   = duration
            item.num_copies = num_copies
            item.save(only = [Item.barcode, Item.num_copies, Item.duration])
            # FIXME if we reduced the number of copies, we need to check loans.
    redirect(f'{dibs.base_url}/list')


@dibs.post('/ready')
@barcode_verified
@authenticated
def toggle_ready():
    '''Set the ready-to-loan field.'''
    barcode = request.POST.barcode.strip()
    if __debug__: log(f'post /ready invoked on barcode {barcode}')
    item = Item.get(Item.barcode == barcode)
    item.ready = not item.ready
    if __debug__: log(f'locking db to change {barcode} ready to {item.ready}')
    with database.atomic('exclusive'):
        item.save(only = [Item.ready])
        # If we removed readiness after the item is let out for loans, we may
        # have to close outstanding loans and remove Recent records.
        if not item.ready:
            num = Loan.delete().where(Loan.item == item).execute()
            if __debug__ and num: log(f'removed {num} loans for {barcode}')
            num = Recent.delete().where(Recent.item == item).execute()
            if __debug__ and num: log(f'removed {num} Recent records for {barcode}')
    redirect(f'{dibs.base_url}/list')


@dibs.post('/remove')
@barcode_verified
@authenticated
def remove_item():
    '''Handle http post request to remove an item from the list page.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        redirect(f'{dibs.base_url}/notallowed')
        return
    barcode = request.POST.barcode.strip()
    item = Item.get(Item.barcode == barcode)
    if __debug__: log(f'locking database to remove {barcode}')
    with database.atomic('exclusive'):
        item.ready = False
        item.save(only = [Item.ready])
        # Clean up loans & recents, but do it 1st, while the item object exists.
        num = Loan.delete().where(Loan.item == item).execute()
        if __debug__ and num: log(f'removed {num} loans for {barcode}')
        num = Recent.delete().where(Recent.item == item).execute()
        if __debug__ and num: log(f'removed {num} Recent records for {barcode}')
        Item.delete().where(Item.barcode == barcode).execute()
    redirect(f'{dibs.base_url}/manage')


# User endpoints.
# .............................................................................

@dibs.get('/')
@dibs.get('/<name:re:(info|welcome|about|thankyou)>')
def general_page(name = '/'):
    '''Display the welcome page.'''
    if __debug__: log(f'get /{"" if name == "/" else name} invoked')
    if name == 'about':
        return page('about')
    elif name == 'thankyou':
        return page('thankyou')
    else:
        return page('info', reloan_wait_time = naturaldelta(_RELOAN_WAIT_TIME))


#FIXME: We need an item status which returns a JSON object
# so the item page can update itself without reloading the whole page.
@dibs.get('/item-status/<barcode:int>')
@expired_loans_removed
@authenticated
def item_status(barcode):
    '''Returns an item summary status as a JSON string'''
    user = request.environ['beaker.session'].get('user')
    if __debug__: log(f'get /item-status invoked on barcode {barcode} and {user}')

    obj = {
        'barcode': barcode,
        'ready': False,
        'available': False,
        'explanation': '',
        'endtime' : None,
        'base_url': dibs.base_url
        }
    item = Item.get_or_none(Item.barcode == barcode)
    if (item != None) and (user != None):
        obj['ready'] = item.ready
        user_loans = list(Loan.select().where(Loan.user == user))
        recent_history = list(Recent.select().where(Recent.item == item))
        endtime = None
        # First check if the user has recently loaned out this same item.
        if any(loan for loan in recent_history if loan.user == user):
            if __debug__: log(f'{user} recently borrowed {barcode}')
            recent = next(loan for loan in recent_history if loan.user == user)
            endtime = recent.nexttime
            obj['available'] = False
            obj['explanation'] = 'It is too soon after the last time you borrowed this book.'
        elif any(user_loans):
            # The user has a current loan. If it's for this title, redirect them
            # to the viewer; if it's for another title, block the loan button.
            if user_loans[0].item == item:
                if __debug__: log(f'{user} already has {barcode}; redirecting to uv')
                obj['explanation'] = 'You currently have borrowed this book.'
            else:
                if __debug__: log(f'{user} already has a loan on something else')
                obj['available'] = False
                endtime = user_loans[0].endtime
                loaned_item = user_loans[0].item
                obj['explanation'] = ('You have another item on loan'
                               + f' ("{loaned_item.title}" by {loaned_item.author})'
                               + ' and it has not yet been returned.')
        else:
            if __debug__: log(f'{user} is allowed to borrow {barcode}')
            loans = list(Loan.select().where(Loan.item == item))
            obj['available'] = item.ready and (len(loans) < item.num_copies)
            if item.ready and not obj['available']:
                endtime = min(loan.endtime for loan in loans)
                obj['explanation'] = 'All available copies are currently on loan.'
            elif not item.ready:
                endtime = None
                obj['explanation'] = 'This item is not currently available through DIBS.'
            else:
                # It's available and they can have it.
                endtime = None
                obj['explanation'] = ''
        if endtime != None:
            obj['endtime'] = human_datetime(endtime)
        else:
            obj['endtime'] == None
    return json.dumps(obj)


@dibs.get('/item/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
def show_item_info(barcode):
    '''Display information about the given item.'''
    user = request.environ['beaker.session'].get('user')
    if __debug__: log(f'get /item invoked on barcode {barcode} by {user}')

    item = Item.get(Item.barcode == barcode)
    user_loans = list(Loan.select().where(Loan.user == user))
    recent_history = list(Recent.select().where(Recent.item == item))
    # First check if the user has recently loaned out this same item.
    if any(loan for loan in recent_history if loan.user == user):
        if __debug__: log(f'{user} recently borrowed {barcode}')
        recent = next(loan for loan in recent_history if loan.user == user)
        endtime = recent.nexttime
        available = False
        explanation = 'It is too soon after the last time you borrowed this book.'
    elif any(user_loans):
        # The user has a current loan. If it's for this title, redirect them
        # to the viewer; if it's for another title, block the loan button.
        if user_loans[0].item == item:
            if __debug__: log(f'{user} already has {barcode}; redirecting to uv')
            redirect(f'{dibs.base_url}/view/{barcode}')
            return
        else:
            if __debug__: log(f'{user} already has a loan on something else')
            available = False
            endtime = user_loans[0].endtime
            loaned_item = user_loans[0].item
            explanation = ('You have another item on loan'
                           + f' ("{loaned_item.title}" by {loaned_item.author})'
                           + ' and it has not yet been returned.')
    else:
        if __debug__: log(f'{user} is allowed to borrow {barcode}')
        loans = list(Loan.select().where(Loan.item == item))
        available = item.ready and (len(loans) < item.num_copies)
        if item.ready and not available:
            endtime = min(loan.endtime for loan in loans)
            explanation = 'All available copies are currently on loan.'
        elif not item.ready:
            endtime = None
            explanation = 'This item is not currently available through DIBS.'
        else:
            # It's available and they can have it.
            # FIXME this can't be right
            endtime = dt.utcnow()
            explanation = None
    return page('item', item = item, available = available,
                endtime = human_datetime(endtime), explanation = explanation)


@dibs.post('/loan')
@expired_loans_removed
@barcode_verified
@authenticated
def loan_item():
    '''Handle http post request to loan out an item, from the item info page.'''
    user = request.environ['beaker.session'].get('user')
    barcode = request.POST.barcode.strip()
    if __debug__: log(f'post /loan invoked on barcode {barcode} by {user}')

    item = Item.get(Item.barcode == barcode)
    if not item.ready:
        # Normally we shouldn't see a loan request through our form if it's not
        # ready, so either staff has changed the status after item was made
        # available or someone got here accidentally (or deliberately).
        if __debug__: log(f'{barcode} is not ready for loans')
        redirect(f'{dibs.base_url}/view/{barcode}')
        return

    # Checking if the item is available requires steps, and we have to be sure
    # that two users don't do them concurrently, or else we might make 2 loans.
    if __debug__: log(f'locking database')
    with database.atomic('exclusive'):
        if any(Loan.select().where(Loan.user == user)):
            if __debug__: log(f'{user} already has a loan on something else')
            return page('error', summary = 'only one loan at a time',
                        message = ('Our policy currently prevents users from '
                                   'borrowing more than one item at a time.'))
        loans = list(Loan.select().where(Loan.item == item))
        if any(loan.user for loan in loans if user == loan.user):
            # Shouldn't be able to reach this point b/c the item page shouldn't
            # make a loan available for this user & item combo. But if
            # something weird happens (e.g., double posting), we might.
            if __debug__: log(f'{user} already has {barcode} loaned out')
            if __debug__: log(f'redirecting {user} to /view for {barcode}')
            redirect(f'{dibs.base_url}/view/{barcode}')
            return
        if len(loans) >= item.num_copies:
            # This shouldn't be possible, but check it anyway.
            if __debug__: log(f'# loans {len(loans)} >= num_copies for {barcode} ')
            redirect(f'{dibs.base_url}/item/{barcode}')
            return
        recent_history = list(Recent.select().where(Recent.item == item))
        if any(loan for loan in recent_history if loan.user == user):
            if __debug__: log(f'{user} recently borrowed {barcode}')
            recent = next(loan for loan in recent_history if loan.user == user)
            return page('error', summary = 'too soon',
                        message = ('We ask that you wait at least '
                                   f'{naturaldelta(_RELOAN_WAIT_TIME)} before '
                                   'requesting the same item again. Please try '
                                   f'after {human_datetime(recent.nexttime)}'))
        # OK, the user is allowed to loan out this item.
        start = dt.utcnow()
        time = delta(minutes = 1) if debug_mode() else delta(hours = item.duration)
        end = start + time
        if __debug__: log(f'creating new loan for {barcode} for {user}')
        Loan.create(item = item, user = user, started = start, endtime = end)

    send_email(user, item, start, end, dibs.base_url)
    redirect(f'{dibs.base_url}/view/{barcode}')


@dibs.post('/return')
@expired_loans_removed
@barcode_verified
@authenticated
def end_loan():
    '''Handle http post request to return the given item early.'''
    barcode = request.forms.get('barcode').strip()
    user = request.environ['beaker.session'].get('user')
    if __debug__: log(f'get /return invoked on barcode {barcode} by {user}')

    loans = list(Loan.select().join(Item).where(Loan.item.barcode == barcode))
    user_loans = [loan for loan in loans if user == loan.user]
    if len(user_loans) > 1:
        # Internal error -- users should not have more than one loan of an
        # item. Right now, we simply log it and move on.
        if __debug__: log(f'error: more than one loan for {barcode} by {user}')
    elif user_loans:
        # Normal case: user has loaned a copy of item. Delete the record
        # and add a new Recent loan record.
        if __debug__: log(f'locking database to delete loan of {barcode} by {user}')
        with database.atomic('immediate'):
            user_loans[0].delete_instance()
            Recent.create(item = Item.get(Item.barcode == barcode), user = user,
                          nexttime = dt.utcnow() + _RELOAN_WAIT_TIME)
    else:
        # User does not have this item loaned out. Ignore the request.
        if __debug__: log(f'{user} does not have {barcode} loaned out')
    redirect(f'{dibs.base_url}/thankyou')


@dibs.get('/view/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
def send_item_to_viewer(barcode):
    '''Redirect to the viewer.'''
    user = request.environ['beaker.session'].get('user')
    if __debug__: log(f'get /view invoked on barcode {barcode} by {user}')

    loans = list(Loan.select().join(Item).where(Loan.item.barcode == barcode))
    user_loans = [loan for loan in loans if user == loan.user]
    if user_loans:
        if __debug__: log(f'redirecting to viewer for {barcode} for {user}')
        endtime = user_loans[0].endtime    # Remember this is in UTC.
        wait_time = delta(minutes = 1) if debug_mode() else _RELOAN_WAIT_TIME
        return page('uv', barcode = barcode,
                    human_endtime = human_datetime(endtime),
                    js_endtime = human_datetime(endtime, '%m/%d/%Y %H:%M:%S'),
                    reloan_wait_time = naturaldelta(wait_time))
    else:
        if __debug__: log(f'{user} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/item/{barcode}')


@dibs.get('/manifests/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
def return_iiif_manifest(barcode):
    '''Return the manifest file for a given item.'''
    user = request.environ['beaker.session'].get('user')
    if __debug__: log(f'get /manifests/{barcode} invoked by {user}')

    loans = list(Loan.select().join(Item).where(Loan.item.barcode == barcode))
    if any(loan.user for loan in loans if user == loan.user):
        manifest_file = join(_MANIFEST_DIR, f'{barcode}-manifest.json')
        if not exists(manifest_file):
            if __debug__: log(f'{manifest_file} does not exist')
            return
        with open(join(_MANIFEST_DIR, f'{barcode}-manifest.json'), 'r') as mf:
            data = mf.read()
            # Change refs to the IIIF server to point to our DIBS route instead.
            content = data.replace(_IIIF_BASE_URL, f'{dibs.base_url}/iiif/{barcode}')
            # Change occurrences of %2F (slashes) in IIIF identifiers to '!' so
            # Apache doesn't auto-convert %2F when UV fetches /iiif/...
            content = content.replace(str(barcode) + r'%2F', f'{barcode}!')
        with NamedTemporaryFile() as new_manifest:
            new_manifest.write(content.encode())
            new_manifest.seek(0)
            if __debug__: log(f'returning manifest for {barcode} for {user}')
            return static_file(new_manifest.name, root = '/')
    else:
        if __debug__: log(f'{user} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/notallowed')
        return


@dibs.get('/iiif/<barcode>/<rest:re:.+>')
@expired_loans_removed
@barcode_verified
@authenticated
def return_iiif_content(barcode, rest):
    '''Return the manifest file for a given item.'''
    user = request.environ['beaker.session'].get('user')
    if __debug__: log(f'get /iiif/{barcode}/{rest} invoked by {user}')

    loans = list(Loan.select().join(Item).where(Loan.item.barcode == barcode))
    if not any(loan.user for loan in loans if user == loan.user):
        if __debug__: log(f'{user} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/notallowed')
        return
    # Undo the temporary encoding done by return_iiif_manifest().
    corrected = rest.replace(f'{barcode}!', str(barcode) + r'%2F')
    url = _IIIF_BASE_URL + '/' + corrected

    # UV uses ajax to get info.json files, which fails if we redirect the
    # requests to the IIIF server. Grab & serve the content ourselves.
    if url.endswith('json'):
        response, error = net('get', url)
        with NamedTemporaryFile() as data_file:
            data_file.write(response.content)
            data_file.seek(0)
            if __debug__: log(f'returning {len(response.content)} bytes for'
                              f' /iiif/{barcode}/{rest}')
            return static_file(data_file.name, root = '/')
    else:
        if __debug__: log(f'redirecting to {url} for {barcode} for {user}')
        redirect(url)


# Universal viewer interface.
# .............................................................................
# The uv subdirectory contains generic html and css.  We serve them as static
# files to anyone; they don't need to be controlled.  The multiple routes
# are because the UV files themselves reference different paths.

@dibs.route('/view/uv/<filepath:path>')
@dibs.route('/viewer/uv/<filepath:path>')
def serve_uv_files(filepath):
    if __debug__: log(f'serving static uv file /viewer/uv/{filepath}')
    return static_file(filepath, root = 'viewer/uv')


# The uv subdirectory contains generic html and css. Serve as static files.
@dibs.route('/viewer/<filepath:path>')
def serve_uv_files(filepath):
    if __debug__: log(f'serving static uv file /viewer/{filepath}')
    return static_file(filepath, root = 'viewer')


# Error pages.
# .............................................................................
# Note: the Bottle session plugin does not seem to supply session arg to @error.

@dibs.get('/notallowed')
@dibs.post('/notallowed')
def not_allowed():
    if __debug__: log(f'serving /notallowed')
    return page('error', summary = 'access error',
                message = ('The requested method does not exist or you do not '
                           'not have permission to access the requested item.'))

@dibs.error(404)
def error404(error):
    if __debug__: log(f'error404 called on {request.path} with {error}')
    return page('404', code = error.status_code, message = error.body)


@dibs.error(405)
def error405(error):
    if __debug__: log(f'error405 called on {request.path} with {error}')
    return page('error', summary = 'method not allowed',
                message = ('The requested method does not exist or you do not '
                           'not have permission to perform the action.'))


# Miscellaneous static pages.
# .............................................................................

@dibs.get('/favicon.ico')
def favicon():
    '''Return the favicon.'''
    if __debug__: log(f'returning favicon')
    return static_file('favicon.ico', root = 'dibs/static')


@dibs.get('/static/<filename:re:[-a-zA-Z0-9]+.(html|jpg|svg|css|js)>')
def included_file(filename):
    '''Return a static file used with %include in a template.'''
    if __debug__: log(f'returning included file {filename}')
    return static_file(filename, root = 'dibs/static')


# Main exported application.
# .............................................................................
# In the file above, we defined a Bottle application and its routes.  Now we
# take that application definition and hand it to a middleware layer for
# session handling (using Beaker).  The new "dibs" constitutes the final
# application that is invoked by the WSGI server via ../adapter.wsgi.

dibs = SessionMiddleware(dibs, _SESSION_CONFIG)
