'''
server.py: DIBS server definition.
'''

from   datetime import datetime, timedelta
from   decouple import config
import bottle
from   bottle import Bottle, HTTPResponse, static_file, template
from   bottle import request, response, redirect, route, get, post, error
from   bottle_session import SessionPlugin
import functools
from   humanize import naturaldelta
import json
import os
from   os.path import realpath, dirname, join
from   peewee import *
import sys
import threading
from   topi import Tind

from .database import Item, Loan, Recent
from .date_utils import human_datetime
from .email import send_email
from .people import Person, check_password, person_from_session
from .roles import role_to_redirect, has_required_role

if __debug__:
    from sidetrack import log, set_debug


# Exported variables.
# .............................................................................

dibs = Bottle()


# Bottle configuration.
# .............................................................................

# Tell Bottle where to find templates.  This is necessary for both the Bottle
# template() command to work and also to get %include to work inside our .tpl
# template files.  Our templates are relative to the current directory but
# Bottle doesn't know that unless we tell it.  Rather surprisingly, the only
# way to do that with Bottle is to set this Bottle package-level variable.
bottle.TEMPLATE_PATH.append(join(realpath(dirname(__file__)), 'templates'))

# Session handling via a Redis-backed database.
dibs.install(SessionPlugin(cookie_name = config('COOKIE_NAME') or 'dibs',
                           cookie_lifetime = config('COOKIE_LIFETIME', cast = int)))


# Internal constants used throughout this file.
# .............................................................................

# Cooling-off period after a loan ends, before user can borrow same title again.
_RELOAN_WAIT_TIME = timedelta(minutes = int(config('RELOAN_WAIT_TIME') or 30))

# Where we send users to give feedback.
_FEEDBACK_URL = config('FEEDBACK_URL') or '/welcome'

# Lock object used around some code to prevent concurrent modification.
_THREAD_LOCK = threading.Lock()


# Decorators used throughout this file.
# .............................................................................

def expired_loans_removed(func):
    '''Clean up expired loans before the function is called.'''
    # FIXME: Checking the loans at every function call is not efficient.  This
    # approach needs to be replaced with something more efficient.
    @functools.wraps(func)
    def expired_loan_removing_wrapper(session, *args, **kwargs):
        for loan in Loan.select():
            if datetime.now() >= loan.endtime:
                barcode = loan.item.barcode
                if __debug__: log(f'creating recent record for {barcode} by {loan.user}')
                Recent.create(item = loan.item, user = loan.user,
                              nexttime = loan.endtime + timedelta(minutes = 1))
                if __debug__: log(f'expiring loan of {barcode} by {loan.user}')
                loan.delete_instance()
        for recent in Recent.select():
            if datetime.now() >= recent.nexttime:
                barcode = recent.item.barcode
                if __debug__: log(f'expiring recent record for {barcode} by {recent.user}')
                recent.delete_instance()
        return func(session, *args, **kwargs)
    return expired_loan_removing_wrapper


def barcode_verified(func):
    '''Check if the given barcode (passed as keyword argument) exists.'''
    @functools.wraps(func)
    def barcode_verification_wrapper(session, *args, **kwargs):
        if 'barcode' in kwargs:
            barcode = kwargs['barcode']
            if not Item.get_or_none(Item.barcode == barcode):
                if __debug__: log(f'there is no item with barcode {barcode}')
                return page('error', session, summary = 'no such barcode',
                            message = f'There is no item with barcode {barcode}.')
        return func(session, *args, **kwargs)
    return barcode_verification_wrapper


def authenticated(func):
    '''Check if the user is authenticated and redirect to /login if not.'''
    @functools.wraps(func)
    def authentication_check_wrapper(session, *args, **kwargs):
        if 'user' not in session or session['user'] is None:
            if __debug__: log(f'user not found in session object')
            redirect(f'{base_url()}/login')
        else:
            if __debug__: log(f'user is authenticated: {session["user"]}')
        return func(session, *args, **kwargs)
    return authentication_check_wrapper


# This next one is needed because some browser plugins seem to cause HTTP HEAD
# calls on web pages you visit.  Bottle routes them to the same defined
# endpoints as GET, which ends up causing our functions to be called twice
# (once for HEAD, once for GET).  It *shouldn't* matter, apart from the extra
# work, but just in case we make a mistake and end up having a GET handler
# also cause side-effects, let's just drop those HEAD calls.

def head_method_ignored(func):
    '''Ignore HTTP HEAD calls on the route.'''
    @functools.wraps(func)
    def ignore_head_method_wrapper(session, *args, **kwargs):
        if request.method == 'HEAD':
            if __debug__: log(f'ignoring HEAD on {request.path}')
            return
        return func(session, *args, **kwargs)
    return ignore_head_method_wrapper


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
def show_login_page(session):
    # NOTE: If SSO is implemented this should redirect to the
    # SSO end point with a return to /login on success.
    if __debug__: log('get /login invoked')
    return page('login', session)


@dibs.post('/login')
def login(session):
    # NOTE: If SSO is implemented this end point will handle the
    # successful login case applying role rules if necessary.
    email = request.forms.get('email').strip()
    password = request.forms.get('password')
    if __debug__: log(f'post /login invoked by {email}')
    # get our person obj from people.db for demo purposes
    user = (Person.get_or_none(Person.uname == email))
    if user != None:
        if check_password(password, user.secret) == False:
            if __debug__: log(f'wrong password -- rejecting {email}')
            return page('login', session)
        else:
            if __debug__: log(f'creating session for {email}')
            session['user'] = email
            p = role_to_redirect(user.role)
            if __debug__: log(f'redirecting to "{p}"')
            redirect(f'{base_url()}/{p}')
            return
    else:
        if __debug__: log(f'wrong password -- rejecting {email}')
        return page('login', session)


@dibs.get('/logout')
@expired_loans_removed
@head_method_ignored
def logout(session):
    if 'user' not in session:
        if __debug__: log(f'get /logout invoked by unauthenticated user')
    else:
        user = session['user']
        if __debug__: log(f'get /logout invoked by {user}')
        del session['user']
    redirect(f'{base_url()}/login')


@dibs.get('/list')
@expired_loans_removed
@head_method_ignored
@authenticated
def list_items(session):
    '''Display the list of known items.'''
    person = person_from_session(session)
    if has_required_role(person, 'library') == False:
        redirect(f'{base_url()}/notallowed')
        return
    if __debug__: log('get /list invoked')
    return page('list', session, items = Item.select())


@dibs.get('/manage')
@expired_loans_removed
@head_method_ignored
@authenticated
def list_items(session):
    '''Display the list of known items.'''
    person = person_from_session(session)
    if has_required_role(person, 'library') == False:
        redirect(f'{base_url()}/notallowed')
        return
    if __debug__: log('get /manage invoked')
    return page('manage', session, items = Item.select())


@dibs.get('/add')
@expired_loans_removed
@authenticated
@head_method_ignored
def add(session):
    '''Display the page to add new items.'''
    person = person_from_session(session)
    if has_required_role(person, 'library') == False:
        redirect(f'{base_url()}/notallowed')
        return
    if __debug__: log('get /add invoked')
    return page('edit', session, action = 'add', item = None)


@dibs.get('/edit/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
@head_method_ignored
def edit(session, barcode):
    '''Display the page to add new items.'''
    person = person_from_session(session)
    if has_required_role(person, 'library') == False:
        redirect(f'{base_url()}/notallowed')
        return
    if __debug__: log(f'get /edit invoked on {barcode}')
    return page('edit', session, action = 'edit',
                item = Item.get(Item.barcode == barcode))


@dibs.post('/update/add')
@dibs.post('/update/edit')
@expired_loans_removed
@authenticated
def update_item(session):
    '''Handle http post request to add a new item from the add-new-item page.'''
    person = person_from_session(session)
    if has_required_role(person, 'library') == False:
        redirect(f'{base_url()}/notallowed')
        return
    if __debug__: log(f'post {request.path} invoked')
    if 'cancel' in request.POST:
        if __debug__: log(f'user clicked Cancel button')
        redirect(f'{base_url()}/list')
        return

    # The HTML form validates the data types, but the POST might come from
    # elsewhere, so we always need to sanity-check the values.
    barcode = request.forms.get('barcode').strip()
    if not barcode.isdigit():
        return page('error', session, summary = 'invalid barcode',
                    message = f'{barcode} is not a valid barcode')
    duration = request.forms.get('duration').strip()
    if not duration.isdigit() or int(duration) <= 0:
        return page('error', session, summary = 'invalid duration',
                    message = f'Duration must be a positive number')
    num_copies = request.forms.get('num_copies').strip()
    if not num_copies.isdigit() or int(num_copies) <= 0:
        return page('error', session, summary = 'invalid copy number',
                    message = f'# of copies must be a positive number')

    # Our current approach only uses items with barcodes that exist in TIND.
    # If that ever changes, the following needs to change too.
    tind = Tind('https://caltech.tind.io')
    try:
        rec = tind.item(barcode = barcode).parent
    except:
        if __debug__: log(f'could not find {barcode} in TIND')
        return page('error', session, summary = 'no such barcode',
                    message = f'There is no item with barcode {barcode}.')
        return

    item = Item.get_or_none(Item.barcode == barcode)
    if '/update/add' in request.path:
        if item:
            if __debug__: log(f'{barcode} already exists in the database')
            return page('error', session, summary = 'duplicate entry',
                        message = f'An item with barcode {{barcode}} already exists.')
        if __debug__: log(f'adding {barcode}, title {rec.title}')
        Item.create(barcode = barcode, title = rec.title, author = rec.author,
                    tind_id = rec.tind_id, year = rec.year,
                    edition = rec.edition, thumbnail = rec.thumbnail_url,
                    num_copies = num_copies, duration = duration)
    else:
        if not item:
            if __debug__: log(f'there is no item with barcode {barcode}')
            return page('error', session, summary = 'no such barcode',
                        message = f'There is no item with barcode {barcode}.')
        if __debug__: log(f'updating {barcode} from {rec}')
	#FIXME: Need to validate these values.
        item.barcode    = barcode
        item.num_copies = num_copies
        item.duration   = duration
	# NOTE: Since we don't have these fields in the edit form we don't
	# go anything with them.
        #for field in ['title', 'author', 'year', 'edition', 'tind_id', 'thumbnail']:
        #    setattr(item, field, getattr(rec, field, ''))
	# NOTE: We only update the specific editable fields.
        item.save(only=[Item.barcode, Item.num_copies, Item.duration])
    redirect(f'{base_url()}/list')


@dibs.post('/ready')
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
    #NOTE: We only save the ready value we toggled.
    item.save(only=[Item.ready])
    if __debug__: log(f'readiness of {barcode} is now {item.ready}')
    # If the readiness state is changed after the item is let out for loans,
    # then there may be outstanding loans right now. Delete them.
    if list(Loan.select(Loan.item == item)):
        if __debug__: log(f'loans for {barcode} have been deleted')
        Loan.delete().where(Loan.item == item).execute()
    redirect(f'{base_url()}/list')


@dibs.post('/remove')
@expired_loans_removed
@barcode_verified
@authenticated
def remove_item(session):
    '''Handle http post request to remove an item from the list page.'''
    person = person_from_session(session)
    if has_required_role(person, 'library') == False:
        redirect(f'{base_url()}/notallowed')
        return
    barcode = request.POST.barcode.strip()
    if __debug__: log(f'post /remove invoked on barcode {barcode}')

    item = Item.get(Item.barcode == barcode)
    item.ready = False
    # Don't forget to delete any loans involving this item.
    if list(Loan.select(Loan.item == item)):
        Loan.delete().where(Loan.item == item).execute()
    Item.delete().where(Item.barcode == barcode).execute()
    redirect(f'{base_url()}/manage')


# User endpoints.
# .............................................................................

@dibs.get('/')
@dibs.get('/info')
@dibs.get('/welcome')
def front_page(session):
    '''Display the welcome page.'''
    if __debug__: log('get / invoked')
    return page('info', session, reloan_wait_time = naturaldelta(_RELOAN_WAIT_TIME))


@dibs.get('/about')
def about_page(session):
    '''Display the welcome page.'''
    if __debug__: log('get /about invoked')
    return page('about', session)

#FIXME: We need an item status which returns a JSON object
# so the item page can update itself without reloading the whole page.
@dibs.get('/item-status/<barcode:int>')
@authenticated
@head_method_ignored
def item_status(session, barcode):
    '''Returns an item summary status as a JSON string'''
    user = session.get('user')
    if __debug__: log(f'get /item-status invoked on barcode {barcode} and {user}')

    obj = {
        'barcode': barcode,
        'ready': False,
        'available': False,
        'explanation': '',
        'endtime' : None,
        'base_url': base_url()
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
@head_method_ignored
def show_item_info(session, barcode):
    '''Display information about the given item.'''
    user = session.get('user')
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
            redirect(f'{base_url()}/view/{barcode}')
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
            endtime = datetime.now()
            explanation = None
    return page('item', session, item = item, available = available,
                endtime = human_datetime(endtime), explanation = explanation)


@dibs.post('/loan')
@expired_loans_removed
@barcode_verified
@authenticated
def loan_item(session):
    '''Handle http post request to loan out an item, from the item info page.'''
    user = session.get('user')
    barcode = request.POST.barcode.strip()
    if __debug__: log(f'post /loan invoked on barcode {barcode} by {user}')

    item = Item.get(Item.barcode == barcode)
    if not item.ready:
        # Normally we shouldn't see a loan request through our form in this
        # case, so either staff has changed the status after item was made
        # available or someone got here accidentally (or deliberately).
        if __debug__: log(f'{barcode} is not ready for loans')
        redirect(f'{base_url()}/view/{barcode}')
        return

    # The default Bottle dev web server is single-thread, so we won't run into
    # the problem of 2 users simultaneously clicking on the loan button.  Other
    # servers are multithreaded, and there's a risk that the time it takes us
    # to look through the loans introduces a window of time when another user
    # might click on the same loan button and cause another loan request to be
    # initiated before the 1st finishes.  So, lock this block of code.
    with _THREAD_LOCK:
        if any(Loan.select().where(Loan.user == user)):
            if __debug__: log(f'{user} already has a loan on something else')
            return page('error', session, summary = 'only one loan at a time',
                        message = ('Our policy currently prevents users from '
                                   'borrowing more than one item at a time.'))
        loans = list(Loan.select().where(Loan.item == item))
        if any(loan.user for loan in loans if user == loan.user):
            # Shouldn't be able to reach this point b/c the item page shouldn't
            # make a loan available for this user & item combo. But if
            # something weird happens (e.g., double posting), we might.
            if __debug__: log(f'{user} already has a copy of {barcode} loaned out')
            if __debug__: log(f'redirecting {user} to /view for {barcode}')
            redirect(f'{base_url()}/view/{barcode}')
            return
        if len(loans) >= item.num_copies:
            # This shouldn't be possible, but catch it anyway.
            if __debug__: log(f'# loans {len(loans)} >= num_copies for {barcode} ')
            redirect(f'{base_url()}/item/{barcode}')
            return
        recent_history = list(Recent.select().where(Recent.item == item))
        if any(loan for loan in recent_history if loan.user == user):
            if __debug__: log(f'{user} recently borrowed {barcode}')
            recent = next(loan for loan in recent_history if loan.user == user)
            return page('error', session, summary = 'too soon',
                        message = ('We ask that you wait at least '
                                   f'{naturaldelta(_RELOAN_WAIT_TIME)} before '
                                   'requesting the same item again. Please try '
                                   f'after {human_datetime(recent.nexttime)}'))
        # OK, the user is allowed to loan out this item.
        start = datetime.now()
        end   = start + timedelta(hours = item.duration)
        if __debug__: log(f'creating new loan for {barcode} for {user}')
        Loan.create(item = item, user = user, started = start, endtime = end)
        send_email(user, item, start, end, base_url())
    redirect(f'{base_url()}/view/{barcode}')


@dibs.get('/return/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
@head_method_ignored
def end_loan(session, barcode):
    '''Handle http get request to return the given item early.'''
    user = session.get('user')
    if __debug__: log(f'get /return invoked on barcode {barcode} by {user}')

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
        Recent.create(item = Item.get(Item.barcode == barcode), user = user,
                      nexttime = datetime.now() + _RELOAN_WAIT_TIME)
    else:
        # User does not have this item loaned out. Ignore the request.
        if __debug__: log(f'{user} does not have {barcode} loaned out')
    redirect(f'{base_url()}/thankyou')


@dibs.get('/view/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
@head_method_ignored
def send_item_to_viewer(session, barcode):
    '''Redirect to the viewer.'''
    user = session.get('user')
    if __debug__: log(f'get /view invoked on barcode {barcode} by {user}')

    loans = list(Loan.select().join(Item).where(Loan.item.barcode == barcode))
    user_loans = [loan for loan in loans if user == loan.user]
    if user_loans:
        if __debug__: log(f'redirecting to viewer for {barcode} for {user}')
        return page('uv', session, barcode = barcode,
                    endtime = human_datetime(user_loans[0].endtime),
                    reloan_wait_time = naturaldelta(_RELOAN_WAIT_TIME))
    else:
        if __debug__: log(f'{user} does not have {barcode} loaned out')
        redirect(f'{base_url()}/item/{barcode}')


@dibs.get('/manifests/<barcode:int>')
@expired_loans_removed
@barcode_verified
@authenticated
@head_method_ignored
def return_manifest(session, barcode):
    '''Return the manifest file for a given item.'''
    user = session.get('user')
    if __debug__: log(f'get /manifests/{barcode} invoked by {user}')

    loans = list(Loan.select().join(Item).where(Loan.item.barcode == barcode))
    if any(loan.user for loan in loans if user == loan.user):
        if __debug__: log(f'returning manifest file for {barcode} for {user}')
        return static_file(f'{barcode}-manifest.json', root = 'manifests')
    else:
        if __debug__: log(f'{user} does not have {barcode} loaned out')
        redirect(f'{base_url()}/notallowed')
        return


@dibs.get('/thankyou')
def say_thank_you(session):
    return page('thankyou', session)


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
def not_allowed(session):
    if __debug__: log(f'serving /notallowed')
    return page('error', session, summary = 'access error',
                message = ('The requested method does not exist or you do not '
                           'not have permission to access the requested item.'))

@error(404)
def error404(error):
    if __debug__: log(f'error404 called with {error}')
    return page('404', None, code = error.status_code, message = error.body)


@error(405)
def error405(error):
    if __debug__: log(f'error405 called with {error}')
    return page('error', session = None, summary = 'method not allowed',
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


# Miscellaneous utilities.
# .............................................................................

def base_url():
    # Bottle is unusual in providing global objects like 'request'.
    parts = request.urlparts
    path  = '' if parts.path == '/' else parts.path
    return f'{parts.scheme}://{parts.netloc}{path}'


def page(name, session, **kargs):
    logged_in = (session and 'user' in session and session['user'] is not None)
    staff_user = has_required_role(person_from_session(session), 'library')
    return template(name, base_url = base_url(), logged_in = logged_in,
                    staff_user = staff_user, feedback_url = _FEEDBACK_URL, **kargs)
