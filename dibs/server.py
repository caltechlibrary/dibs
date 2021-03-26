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
from   enum import Enum, auto
import functools
from   humanize import naturaldelta
import json
import os
from   os.path import realpath, dirname, join, exists
from   peewee import *
import random
import ratelimit
from   sidetrack import log, logr, set_debug
import string
import sys
from   tempfile import NamedTemporaryFile
from   topi import Tind

from .database import Item, Loan, History, database
from .date_utils import human_datetime
from .email import send_email
from .people import Person, check_password, person_from_session
from .roles import role_to_redirect, has_required_role


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
    staff_user = has_required_role(person_from_session(session), 'library')
    return template(name, base_url = dibs.base_url, logged_in = logged_in,
                    staff_user = staff_user, feedback_url = _FEEDBACK_URL, **kargs)


def time_now():
    '''Return datetime.utcnow() but with seconds and microseconds zeroed out.'''
    return dt.utcnow().replace(microsecond = 0)


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
        now = time_now()
        # Delete expired loan recency records.
        for loan in Loan.select().where(Loan.state == 'recent', now >= Loan.reloan_time):
            log(f'locking db to expire loan by {loan.user} on {loan.item.barcode}')
            with database.atomic('immediate'):
                loan.delete_instance()
        # Change the state of active loans that are past due.
        for loan in Loan.select().where(Loan.state == 'active', now >= Loan.end_time):
            barcode = loan.item.barcode
            log(f'locking db to update loan state of {barcode} for {loan.user}')
            with database.atomic('immediate'):
                loan.state = 'recent'
                loan.reloan_time = loan.end_time + _RELOAN_WAIT_TIME
                loan.save(only = [Loan.state, Loan.reloan_time])
                History.create(type = 'loan', what = loan.item.barcode,
                               start_time = loan.start_time, end_time = loan.end_time)
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
        elif request.forms.get('barcode', None):
            barcode = request.forms.get('barcode').strip()
        if barcode: log(f'verifying barcode {barcode}')
        if barcode and not Item.get_or_none(Item.barcode == barcode):
            log(f'there is no item with barcode {barcode}')
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
            log(f'returning empty HEAD on {request.path}')
            return
        session = request.environ['beaker.session']
        if not session.get('user', None):
            log(f'user not found in session object')
            redirect(f'{dibs.base_url}/login')
        else:
            log(f'user is authenticated: {session["user"]}')
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
            log(f'rate limit exceeded for client {client}')
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
    log('get /login invoked')
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
    log(f'post /login invoked by {email}')
    # get our person obj from people.db for demo purposes
    user = Person.get_or_none(Person.uname == email)
    if not user:
        log(f'unknown user -- rejecting {email}')
        return page('login', login_failed = True)
    elif check_password(password, user.secret) == False:
        log(f'wrong password -- rejecting {email}')
        return page('login', login_failed = True)
    else:
        session = request.environ['beaker.session']
        session['user'] = email
        p = role_to_redirect(user.role)
        log(f'created session for {email} & redirecting to {dibs.base_url}/{p}')
        redirect(f'{dibs.base_url}/{p}')


@dibs.post('/logout')
def logout():
    '''Handle the logout action from the navbar menu on every page.'''
    session = request.environ['beaker.session']
    if not session.get('user', None):
        log(f'post /logout invoked by unauthenticated user')
        return
    user = session['user']
    log(f'post /logout invoked by {user}')
    del session['user']
    redirect(f'{dibs.base_url}/login')


@dibs.get('/list')
@expired_loans_removed
@authenticated
def list_items():
    '''Display the list of known items.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        log(f'get /list invoked by non-library user')
        redirect(f'{dibs.base_url}/notallowed')
        return
    log('get /list invoked')
    return page('list', items = Item.select())


@dibs.get('/manage')
@authenticated
def list_items():
    '''Display the list of known items.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        log(f'get /manage invoked by non-library user')
        redirect(f'{dibs.base_url}/notallowed')
        return
    log('get /manage invoked')
    return page('manage', items = Item.select())


@dibs.get('/add')
@authenticated
def add():
    '''Display the page to add new items.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        log(f'get /add invoked by non-library user')
        redirect(f'{dibs.base_url}/notallowed')
        return
    log('get /add invoked')
    return page('edit', action = 'add', item = None)


@dibs.get('/edit/<barcode:int>')
@barcode_verified
@authenticated
def edit(barcode):
    '''Display the page to add new items.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        log(f'get /edit invoked by non-library user')
        redirect(f'{dibs.base_url}/notallowed')
        return
    log(f'get /edit invoked on {barcode}')
    return page('edit', action = 'edit', item = Item.get(Item.barcode == barcode))


@dibs.post('/update/add')
@dibs.post('/update/edit')
@expired_loans_removed
@authenticated
def update_item():
    '''Handle http post request to add a new item from the add-new-item page.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        log(f'post /update invoked by non-library user')
        redirect(f'{dibs.base_url}/notallowed')
        return
    log(f'post {request.path} invoked')
    if 'cancel' in request.POST:
        log(f'user clicked Cancel button')
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
            log(f'{barcode} already exists in the database')
            return page('error', summary = 'duplicate entry',
                        message = f'An item with barcode {barcode} already exists.')
        # Our current approach only uses items with barcodes that exist in
        # TIND.  If that ever changes, the following needs to change too.
        tind = Tind('https://caltech.tind.io')
        try:
            rec = tind.item(barcode = barcode).parent
        except:
            log(f'could not find {barcode} in TIND')
            return page('error', summary = 'no such barcode',
                        message = f'There is no item with barcode {barcode}.')
        log(f'locking db to add {barcode}, title {rec.title}')
        with database.atomic():
            Item.create(barcode = barcode, title = rec.title, author = rec.author,
                        tind_id = rec.tind_id, year = rec.year,
                        edition = rec.edition, thumbnail = rec.thumbnail_url,
                        num_copies = num_copies, duration = duration)
    else: # The operation is /update/edit.
        if not item:
            log(f'there is no item with barcode {barcode}')
            return page('error', summary = 'no such barcode',
                        message = f'There is no item with barcode {barcode}.')
        log(f'locking db to save changes to {barcode}')
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
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        log(f'post /ready invoked by non-library user')
        redirect(f'{dibs.base_url}/notallowed')
        return
    barcode = request.POST.barcode.strip()
    log(f'post /ready invoked on barcode {barcode}')
    item = Item.get(Item.barcode == barcode)
    item.ready = not item.ready
    log(f'locking db to change {barcode} ready to {item.ready}')
    with database.atomic('exclusive'):
        item.save(only = [Item.ready])
        # If we are removing readiness, we may have to close outstanding
        # loans.  Doesn't matter if these are active or recent loans.
        if not item.ready:
            for loan in Loan.select().where(Loan.item == item):
                log(f'deleting {loan.state} loan for {barcode}')
                History.create(type = 'loan', what = loan.item.barcode,
                               start_time = loan.start_time, end_time = loan.end_time)
                loan.delete_instance()
    redirect(f'{dibs.base_url}/list')


@dibs.post('/remove')
@barcode_verified
@authenticated
def remove_item():
    '''Handle http post request to remove an item from the list page.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        log(f'post /remove invoked by non-library user')
        redirect(f'{dibs.base_url}/notallowed')
        return
    barcode = request.POST.barcode.strip()
    item = Item.get(Item.barcode == barcode)
    log(f'locking db to remove {barcode}')
    with database.atomic('exclusive'):
        item.ready = False
        item.save(only = [Item.ready])
        # First clean up loans while we still have the item object.
        for loan in Loan.select().where(Loan.item == item):
            log(f'deleting {loan.state} loan for {barcode}')
            History.create(type = 'loan', what = loan.item.barcode,
                           start_time = loan.start_time, end_time = loan.end_time)
            loan.delete_instance()
        Item.delete().where(Item.barcode == barcode).execute()
    redirect(f'{dibs.base_url}/manage')


@dibs.get('/stats')
@dibs.get('/status')
@authenticated
def show_stats():
    '''Display the list of known items.'''
    person = person_from_session(request.environ['beaker.session'])
    if has_required_role(person, 'library') == False:
        log(f'get /stats invoked by non-library user')
        redirect(f'{dibs.base_url}/notallowed')
        return
    log('get /stats invoked')
    usage_data = []
    for item in Item.select():
        barcode = item.barcode
        active = Loan.select().where(Loan.item == item, Loan.state == 'active').count()
        history = History.select().where(History.what == barcode, History.type == 'loan')
        durations = [(loan.end_time - loan.start_time) for loan in history]
        if durations:
            avg_duration = sum(durations, delta()) // len(durations)
            if avg_duration < delta(seconds = 30):
                avg_duration = '< 30 seconds'
            else:
                avg_duration = naturaldelta(avg_duration)
        else:
            avg_duration = '(never borrowed)'
        usage_data.append((item, active, len(durations), avg_duration))
    return page('stats', usage_data = usage_data)


# User endpoints.
# .............................................................................

# An operation common to several routes is to test if the user can borrow an
# item, and provide the user with feedback if it's not.  The possible cases
# are captured by this next enumeration, and the following helper function
# assesses the current status and returns additional info (as multiple values).

class Status(Enum):
    NOT_READY      = auto()         # Item.ready is False
    NO_COPIES_LEFT = auto()         # No copies left to loan
    LOANED_BY_USER = auto()         # Already loaned by user
    TOO_SOON       = auto()         # Too soon after user's last loan of this
    USER_HAS_OTHER = auto()         # User has another active loan
    AVAILABLE      = auto()         # Available to this user
    UNKNOWN_ITEM   = auto()         # Barcode is not in the DIBS database.


def loan_availability(user, barcode):
    '''Return multiple values: (item, status, explanation, when_available).'''

    item = Item.get_or_none(Item.barcode == barcode)
    if not item:
        log(f'unknown barcode {barcode}')
        status = Status.UNKNOWN_ITEM
        explanation = 'This item is not known to DIBS.'
        return None, status, explanation, None
    if not item.ready:
        log(f'{barcode} is not ready for loans')
        status = Status.NOT_READY
        explanation = 'This item is not available for borrowing at this time.'
        return item, status, explanation, None

    # Start by checking if the user has any active or recent loans.
    explanation = ''
    when_available = None
    loan = Loan.get_or_none(Loan.user == user, Loan.item == item)
    if loan:
        if loan.state == 'active':
            log(f'{user} already has {barcode} on loan')
            status = Status.LOANED_BY_USER
            explanation = 'This is currently on digital loan to you.'
        else:
            log(f'{user} had a loan on {barcode} too recently')
            status = Status.TOO_SOON
            explanation = 'It is too soon after the last time you borrowed it.'
            when_available = loan.reloan_time
    else:
        loan = Loan.get_or_none(Loan.user == user, Loan.state == 'active')
        if loan:
            other = loan.item
            log(f'{user} has a loan on another item: {other.barcode}')
            status = Status.USER_HAS_OTHER
            author = other.author[:50]+"..." if len(other.author) > 50 else other.author
            explanation = ('You have another item currently on loan'
                           + f' ("{other.title}" by {author})')
            when_available = loan.end_time
        else:
            # The user may be allowed to loan this, but are there any copies left?
            loans = list(Loan.select().where(Loan.item == item, Loan.state == 'active'))
            if len(loans) == item.num_copies:
                log(f'all copies of {barcode} are currently loaned')
                status = Status.NO_COPIES_LEFT
                explanation = 'All available copies are currently on loan.'
                when_available = min(loan.end_time for loan in loans)
            else:
                log(f'{user} is allowed to borrow {barcode}')
                status = Status.AVAILABLE

    return item, status, explanation, when_available


@dibs.get('/')
@dibs.get('/<name:re:(info|welcome|about|thankyou)>')
def general_page(name = '/'):
    '''Display the welcome page.'''
    log(f'get /{"" if name == "/" else name} invoked')
    if name == 'about':
        return page('about')
    elif name == 'thankyou':
        return page('thankyou')
    else:
        return page('info', reloan_wait_time = naturaldelta(_RELOAN_WAIT_TIME))


# Next one is used by the item page to update itself w/o reloading whole page.

@dibs.get('/item-status/<barcode:int>')
@expired_loans_removed
@authenticated
def item_status(barcode):
    '''Returns an item summary status as a JSON string'''
    user = request.environ['beaker.session'].get('user')
    log(f'get /item-status invoked on barcode {barcode} and {user}')

    item, status, explanation, when_available = loan_availability(user, barcode)
    return json.dumps({'available'     : (status == Status.AVAILABLE),
                       'explanation'   : explanation,
                       'when_available': human_datetime(when_available)})


@dibs.get('/item/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
def show_item_info(barcode):
    '''Display information about the given item.'''
    user = request.environ['beaker.session'].get('user')
    log(f'get /item invoked on barcode {barcode} by {user}')

    item, status, explanation, when_available = loan_availability(user, barcode)
    if status == Status.LOANED_BY_USER:
        log(f'redirecting {user} to uv for {barcode}')
        redirect(f'{dibs.base_url}/view/{barcode}')
        return
    return page('item', item = item, available = (status == Status.AVAILABLE),
                when_available = human_datetime(when_available),
                explanation = explanation)


@dibs.post('/loan')
@expired_loans_removed
@barcode_verified
@authenticated
def loan_item():
    '''Handle http post request to loan out an item, from the item info page.'''
    user = request.environ['beaker.session'].get('user')
    barcode = request.POST.barcode.strip()
    log(f'post /loan invoked on barcode {barcode} by {user}')

    # Checking if the item is available requires steps, and we have to be sure
    # that two users don't do them concurrently, or else we might make 2 loans.
    log(f'locking db')
    with database.atomic('exclusive'):
        item, status, explanation, when_available = loan_availability(user, barcode)
        if status == Status.NOT_READY:
            # Normally we shouldn't see a loan request through this form if the
            # item is not ready, so either staff changed the status after the
            # item was made available or someone got here accidentally.
            log(f'redirecting {user} back to item page for {barcode}')
            redirect(f'{dibs.base_url}/item/{barcode}')
            return
        if status == Status.LOANED_BY_USER:
            # Shouldn't be able to reach this point b/c the item page
            # shouldn't make a loan available for this user & item combo.
            # But if something weird happens, we might.
            log(f'redirecting {user} to {dibs.base_url}/view/{barcode}')
            redirect(f'{dibs.base_url}/view/{barcode}')
            return
        if status == Status.USER_HAS_OTHER:
            return page('error', summary = 'only one loan at a time',
                        message = ('Our policy currently prevents users from '
                                   'borrowing more than one item at a time.'))
        if status == Status.TOO_SOON:
            loan = Loan.get_or_none(Loan.user == user, Loan.item == item)
            return page('error', summary = 'too soon',
                        message = ('We ask that you wait at least '
                                   f'{naturaldelta(_RELOAN_WAIT_TIME)} before '
                                   'requesting the same item again. Please try '
                                   f'after {human_datetime(when_available)}'))
        if status == Status.NO_COPIES_LEFT:
            # The loan button shouldn't have been clickable in this case, but
            # someone else might have gotten the loan between the last status
            # check and the user clicking it.
            log(f'redirecting {user} to {dibs.base_url}/view/{barcode}')
            redirect(f'{dibs.base_url}/view/{barcode}')
            return

        # OK, the user is allowed to loan out this item.
        time = delta(hours = item.duration)
        start = time_now()
        end = start + time
        reloan = end + _RELOAN_WAIT_TIME
        log(f'creating new loan for {barcode} for {user}')
        Loan.create(item = item, state = 'active', user = user,
                    start_time = start, end_time = end, reloan_time = reloan)

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
    log(f'get /return invoked on barcode {barcode} by {user}')

    item = Item.get(Item.barcode == barcode)
    loan = Loan.get_or_none(Loan.item == item, Loan.user == user)
    if loan and loan.state == 'active':
        # Normal case: user has loaned a copy of item. Update to 'recent'.
        log(f'locking db to change state of loan of {barcode} by {user}')
        with database.atomic('immediate'):
            now = time_now()
            loan.state = 'recent'
            loan.end_time = now
            loan.reloan_time = now + _RELOAN_WAIT_TIME
            loan.save(only = [Loan.state, Loan.end_time, Loan.reloan_time])
            History.create(type = 'loan', what = loan.item.barcode,
                           start_time = loan.start_time, end_time = loan.end_time)
        redirect(f'{dibs.base_url}/thankyou')
    else:
        log(f'{user} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/item/{barcode}')


@dibs.get('/view/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
def send_item_to_viewer(barcode):
    '''Redirect to the viewer.'''
    user = request.environ['beaker.session'].get('user')
    log(f'get /view invoked on barcode {barcode} by {user}')

    item = Item.get(Item.barcode == barcode)
    loan = Loan.get_or_none(Loan.item == item, Loan.user == user)
    if loan and loan.state == 'active':
        log(f'redirecting to viewer for {barcode} for {user}')
        wait_time = _RELOAN_WAIT_TIME
        return page('uv', barcode = barcode,
                    end_time = human_datetime(loan.end_time),
                    js_end_time = human_datetime(loan.end_time, '%m/%d/%Y %H:%M:%S'),
                    wait_time = naturaldelta(wait_time))
    else:
        log(f'{user} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/item/{barcode}')


@dibs.get('/manifests/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
def return_iiif_manifest(barcode):
    '''Return the manifest file for a given item.'''
    user = request.environ['beaker.session'].get('user')
    log(f'get /manifests/{barcode} invoked by {user}')

    item = Item.get(Item.barcode == barcode)
    loan = Loan.get_or_none(Loan.item == item, Loan.user == user)
    if loan and loan.state == 'active':
        manifest_file = join(_MANIFEST_DIR, f'{barcode}-manifest.json')
        if not exists(manifest_file):
            log(f'{manifest_file} does not exist')
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
            log(f'returning manifest for {barcode} for {user}')
            return static_file(new_manifest.name, root = '/')
    else:
        log(f'{user} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/notallowed')
        return


@dibs.get('/iiif/<barcode>/<rest:re:.+>')
@expired_loans_removed
@barcode_verified
@authenticated
def return_iiif_content(barcode, rest):
    '''Return the manifest file for a given item.'''
    user = request.environ['beaker.session'].get('user')
    log(f'get /iiif/{barcode}/{rest} invoked by {user}')

    item = Item.get(Item.barcode == barcode)
    loan = Loan.get_or_none(Loan.item == item, Loan.user == user)
    if loan and loan.state == 'active':
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
                log(f'returning {len(response.content)} bytes for /iiif/{barcode}/{rest}')
                return static_file(data_file.name, root = '/')
        else:
            log(f'redirecting to {url} for {barcode} for {user}')
            redirect(url)
    else:
        log(f'{user} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/notallowed')


# Universal viewer interface.
# .............................................................................
# The uv subdirectory contains generic html and css.  We serve them as static
# files to anyone; they don't need to be controlled.  The multiple routes
# are because the UV files themselves reference different paths.

@dibs.route('/view/uv/<filepath:path>')
@dibs.route('/viewer/uv/<filepath:path>')
def serve_uv_files(filepath):
    log(f'serving static uv file /viewer/uv/{filepath}')
    return static_file(filepath, root = 'viewer/uv')


# The uv subdirectory contains generic html and css. Serve as static files.
@dibs.route('/viewer/<filepath:path>')
def serve_uv_files(filepath):
    log(f'serving static uv file /viewer/{filepath}')
    return static_file(filepath, root = 'viewer')


# Error pages.
# .............................................................................
# Note: the Bottle session plugin does not seem to supply session arg to @error.

@dibs.get('/notallowed')
@dibs.post('/notallowed')
def not_allowed():
    log(f'serving /notallowed')
    return page('error', summary = 'access error',
                message = ('The requested page does not exist or you do not '
                           'not have permission to access the requested item.'))

@dibs.error(404)
def error404(error):
    log(f'{request.method} called on {request.path}, resulting in {error}')
    return page('404', code = error.status_code, message = error.body)


@dibs.error(405)
def error405(error):
    log(f'{request.method} called on {request.path}, resulting in {error}')
    return page('error', summary = 'method not allowed',
                message = ('The requested method does not exist or you do not '
                           'not have permission to perform the action.'))


# Miscellaneous static pages.
# .............................................................................

@dibs.get('/favicon.ico')
def favicon():
    '''Return the favicon.'''
    log(f'returning favicon')
    return static_file('favicon.ico', root = 'dibs/static')


@dibs.get('/static/<filename:re:[-a-zA-Z0-9]+.(html|jpg|svg|css|js|json)>')
def included_file(filename):
    '''Return a static file used with %include in a template.'''
    log(f'returning included file {filename}')
    return static_file(filename, root = 'dibs/static')


# Main exported application.
# .............................................................................
# In the file above, we defined a Bottle application and its routes.  Now we
# take that application definition and hand it to a middleware layer for
# session handling (using Beaker).  The new "dibs" constitutes the final
# application that is invoked by the WSGI server via ../adapter.wsgi.

dibs = SessionMiddleware(dibs, _SESSION_CONFIG)
