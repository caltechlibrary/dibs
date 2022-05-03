'''
server.py: DIBS server definition.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

import bottle
from   bottle import Bottle, LocalResponse, static_file, template
from   bottle import request, response, redirect
from   commonpy.file_utils import delete_existing
from   commonpy.network_utils import net
from   datetime import timedelta as delta
from   enum import Enum, auto
from   expiringdict import ExpiringDict
from   fdsend import send_file
from   humanize import naturaldelta, naturalsize
import inspect
from   io import BytesIO, StringIO
import json
from   lru import LRU
import os
from   os.path import realpath, dirname, join, exists
from   peewee import PeeweeException
from   playhouse.dataset import DataSet
from   playhouse.reflection import generate_models
from   sidetrack import log
from   str2bool import str2bool
from   textwrap import shorten
from   trinomial import anon

from . import __version__
from .data_models import database, Item, Loan, History, Person
from .date_utils import human_datetime, round_minutes, time_now
from .email import send_email
from .image_utils import as_jpeg
from .lsp import LSP
from .people import person_from_environ, GuestPerson
from .roles import staff_user
from .settings import config, resolved_path


# General configuration and initialization.
# .............................................................................

# Begin by creating a Bottle object on which we will define routes and other
# behaviors in the rest of this file.
dibs = Bottle()

# Construct the path to the server root, which we use to construct other paths.
_SERVER_ROOT = realpath(join(dirname(__file__), os.pardir))

# Tell Bottle where to find templates.  This is necessary for both the Bottle
# template() command to work and also to get %include to work inside our .tpl
# template files.  Rather surprisingly, the only way to tell Bottle where to
# find the templates is to set this Bottle package-level variable.
bottle.TEMPLATE_PATH.append(join(_SERVER_ROOT, 'dibs', 'templates'))

# Directory containing IIIF manifest files.
_MANIFEST_DIR = resolved_path(config('MANIFEST_DIR'))

# Directory containing workflow processing status files.
_PROCESS_DIR = resolved_path(config('PROCESS_DIR'))

# Directory containing thumbnail images of item covers/jackets.
_THUMBNAILS_DIR = resolved_path(config('THUMBNAILS_DIR'))

# Internal threshold for max size of thumbnail images uploaded via edit form.
_MAX_THUMBNAIL_SIZE = 1 * 1024 * 1024

# The base URL of the IIIF server endpoint.
_IIIF_BASE_URL = config('IIIF_BASE_URL')

# Cooling-off period after a loan ends, before user can borrow same title again.
# Set it to 1 minute in debug mode. (Note: can't check dibs.debug_mode here b/c
# when this file is loaded, it's not yet set.  Test a Bottle variable instead.)
_RELOAN_WAIT_TIME = (delta(minutes = 1) if ('BOTTLE_CHILD' in os.environ)
                     else delta(minutes = int(config('RELOAN_WAIT_TIME'))))

# Where we send users to give feedback.
_FEEDBACK_URL = config('FEEDBACK_URL')

# Where we send users for help.  The default is the DIBS software documentation
# page, which is assumed to exist even if individual sites don't provide docs.
_HELP_URL = config('HELP_URL', default = 'https://caltechlibrary.github.io/dibs')

# If there's a site announcement file, this will be its path.
_SITE_ANNOUNCEMENT_FILE = join(_SERVER_ROOT, 'site-announcement.html')

# Remember the most recent accesses so we can provide stats on recent activity.
# This is a dictionary whose elements are dictionaries.
_REQUESTS = {'15': ExpiringDict(max_len = 1000000, max_age_seconds = 15*60),
             '30': ExpiringDict(max_len = 1000000, max_age_seconds = 30*60),
             '45': ExpiringDict(max_len = 1000000, max_age_seconds = 45*60),
             '60': ExpiringDict(max_len = 1000000, max_age_seconds = 60*60)}

# IIIF page cache.  This is a dict where the keys will be IIIF page URLs.
_IIIF_CACHE = LRU(int(config('IIIF_CACHE_SIZE')))


# General-purpose utilities used repeatedly.
# .............................................................................

def page(name, **kargs):
    '''Create a page using template "name" with some standard variables set.'''
    person = person_from_environ(request.environ)
    logged_in = (person is not None and person.uname != '')
    if kargs.get('browser_no_cache', False):
        response.add_header('Expires', '0')
        response.add_header('Pragma', 'no-cache')
        response.add_header('Cache-Control',
                            'no-store, max-age=0, no-cache, must-revalidate')
    announcement = None
    if exists(_SITE_ANNOUNCEMENT_FILE):
        with open(_SITE_ANNOUNCEMENT_FILE, 'r') as f:
            announcement = f.read().strip()
        if len(announcement) == 0:
            announcement = None
    return template(name, base_url = dibs.base_url, version = __version__,
                    logged_in = logged_in, staff_user = staff_user(person),
                    announcement = announcement,
                    feedback_url = _FEEDBACK_URL, help_url = _HELP_URL,
                    reloan_wait_time = naturaldelta(_RELOAN_WAIT_TIME), **kargs)


def record_request(barcode):
    '''Record requests for content related to barcode.'''
    # The expiring dict takes care of everthing -- we just need to add entries.
    _REQUESTS['15'][barcode] = _REQUESTS['15'].get(barcode, 0) + 1
    _REQUESTS['30'][barcode] = _REQUESTS['30'].get(barcode, 0) + 1
    _REQUESTS['45'][barcode] = _REQUESTS['45'].get(barcode, 0) + 1
    _REQUESTS['60'][barcode] = _REQUESTS['60'].get(barcode, 0) + 1


def debug_mode():
    '''Return True if we're running Bottle's default server in debug mode.'''
    return getattr(dibs, 'debug_mode', False)


def urls_rerouted(text, barcode):
    '''Rewrite text to point IIIF URLs to our /iiif endpoint & fix some issues.'''
    barcode = str(barcode)
    rewritten = text.replace(_IIIF_BASE_URL, f'{dibs.base_url}/iiif/{barcode}')
    # Change occurrences of %2F (slashes) in IIIF identifiers to '!' so
    # Apache doesn't auto-convert %2F when UV fetches /iiif/...
    return rewritten.replace(barcode + r'%2F', f'{barcode}!')


def urls_restored(text, barcode):
    '''Reverse the transformations made by urls_rerouted(...).'''
    barcode = str(barcode)
    rewritten = text.replace(f'{barcode}!', barcode + r'%2F')
    return rewritten.replace(f'{dibs.base_url}/iiif/{barcode}', _IIIF_BASE_URL)


def user(person):
    if isinstance(person, (Person, GuestPerson)):
        if person.uname:
            return 'user ' + anon(person.uname)
        else:
            return 'guest user'
    elif isinstance(person, str):
        return 'user ' + anon(person)
    else:
        return 'unknown user'


# Bespoke, locally-sourced, artisanal Bottle plugins.
# .............................................................................
# Bottle's "plugins" are basically like Python decorators.  They're most
# useful when you have a decorator that you would otherwise want to put on
# every route (and which would therefore clutter your source code with a lot
# of repetitive calls to @foo decorators).  Bottle calls the plugins in the
# Bottle @get/@post/@route functions, and like Python decorators, a given
# plugin is only applied once to a given route (because what a plugin does is
# wrap a function with another function).  Tip: if you also have decorators
# that you want be added to a route, put the decorators highest, above the
# call to @dibs.get/@dibs.post.

class BottlePluginBase():
    '''Base class for Bottle plugins for DIBS.'''
    # This sets the Bottle API version. It defaults to v.1. See
    # https://bottlepy.org/docs/dev/plugindev.html#plugin-api-changes
    api = 2


class DatabaseConnector(BottlePluginBase):
    '''Wrap a route with a connection to the database.'''
    def __call__(self, callback):
        def database_connector(*args, **kwargs):
            log('opening database connection')
            database.connect()
            try:
                result = callback(*args, **kwargs)
                database.commit()
            except PeeweeException as ex:
                log('*** database exception: ' + str(ex))
            finally:
                log('closing database connection')
                database.close()
            return result

        return database_connector


class LoanExpirer(BottlePluginBase):
    '''Wrap every route function with code that expires loans as needed.'''

    # Expiring loans every time any route is invoked is inefficient, but this
    # approach has the advantage of simplicity in a multi-process Apache server
    # config.  The alternative would be to implement a separate reaper process,
    # complicating things significantly.  (If we only had to worry about
    # multiple threads, it would be easier, but our httpd runs processes.)

    def __call__(self, callback):
        def loan_expirer(*args, **kwargs):
            now = time_now()
            # Delete expired loan recency records.
            log('checking for expired loans')
            n = Loan.delete().where(Loan.state == 'recent', now >= Loan.reloan_time).execute()
            if n > 0:
                log(f'deleted {n} recent loans that reached their reloan times')
            # Change the state of active loans that are past due.
            loans = Loan.select().where(Loan.state == 'active', now >= Loan.end_time)
            if len(loans) > 0:
                log('locking db to update loan states')
                with database.atomic('immediate'):
                    for loan in loans:
                        barcode = loan.item.barcode
                        log(f'updating {barcode} loan state for {user(loan.user)}')
                        next_time = loan.end_time + _RELOAN_WAIT_TIME
                        loan.reloan_time = round_minutes(next_time, 'down')
                        loan.state = 'recent'
                        loan.save(only = [Loan.state, Loan.reloan_time])
                        # Don't count staff users in stats except in debug mode
                        if staff_user(loan.user) and not debug_mode():
                            continue
                        History.create(type = 'loan', what = barcode,
                                       start_time = loan.start_time,
                                       end_time = loan.end_time)
            return callback(*args, **kwargs)

        return loan_expirer


class BarcodeVerifier(BottlePluginBase):
    '''Check barcode validity in routes that have a "barcode" parameter.'''

    def apply(self, callback, route):
        args = inspect.getfullargspec(route.callback)[0]
        if 'barcode' not in args:
            return callback

        def barcode_verifier(*args, **kwargs):
            # This handles both HTTP GET & POST requests.  In the case of GET,
            # there will be an argument to the function called "barcode"; in
            # the case of POST, there will be a form variable called "barcode".
            log('running barcode verifier')
            barcode = None
            if 'barcode' in kwargs:
                barcode = kwargs['barcode']
            elif 'barcode' in request.POST:
                barcode = request.POST.barcode.strip()
            elif request.forms.get('barcode', None):
                barcode = request.forms.get('barcode').strip()
            if barcode and not Item.get_or_none(Item.barcode == barcode):
                log(f'there is no item with barcode {barcode}')
                return page('error', summary = 'no such barcode',
                            message = f'There is no item with barcode {barcode}.')
            return callback(*args, **kwargs)

        return barcode_verifier


class RouteTracer(BottlePluginBase):
    '''Write a log entry for this route invocation.'''

    def apply(self, callback, route):
        # Minor optimization: only install this if we're running in debug mode.
        if not debug_mode():
            return callback

        def route_tracer(*args, **kwargs):
            barcode = None
            if 'barcode' in kwargs:
                barcode = kwargs['barcode']
            elif 'barcode' in request.POST:
                barcode = request.POST.barcode.strip()
            elif request.forms.get('barcode', None):
                barcode = request.forms.get('barcode').strip()
            who = request.environ['REMOTE_USER']
            log(f'{user(who)} invoked {route.method.lower()} {route.rule}'
                + (f' for {barcode}' if barcode else ''))
            return callback(*args, **kwargs)

        return route_tracer


# Hook in the plugins above into all routes. The order here matters: the first
# one added here becomes the first one called.

dibs.install(DatabaseConnector())
dibs.install(RouteTracer())
dibs.install(BarcodeVerifier())
dibs.install(LoanExpirer())


# The remaining plugins below are applied selectively to specific routes only.


class AddPersonArgument(BottlePluginBase):
    '''Inject a 'person' keyword to the arguments of a route function.'''
    def apply(self, callback, route):
        def person_plugin_wrapper(*args, **kwargs):
            person = person_from_environ(request.environ)
            if person is None or person.uname is None:
                log('person is None')
                return page('error', summary = 'authentication failure',
                            message = 'Unrecognized user identity.')
            if 'person' in inspect.getfullargspec(route.callback)[0]:
                kwargs['person'] = person
            return callback(*args, **kwargs)
        return person_plugin_wrapper


class VerifyStaffUser(BottlePluginBase):
    '''Redirect to an error page if the user lacks sufficient priviledges.'''
    def apply(self, callback, route):
        def staff_person_plugin_wrapper(*args, **kwargs):
            person = person_from_environ(request.environ)
            if person is None:
                log('person is None')
                return page('error', summary = 'authentication failure',
                            message = 'Unrecognized user identity.')
            if not staff_user(person):
                log(f'{request.path} invoked by non-staff {user(person)}')
                redirect(f'{dibs.base_url}/notallowed')
                return
            return callback(*args, **kwargs)
        return staff_person_plugin_wrapper


# Administrative interface endpoints.
# .............................................................................

# A note about authentication: the entire DIBS application is assumed to be
# behind a server that implements authentication, for example using SSO.
# This means we never need to log a person in: they will be authenticated by
# SSO before they can get to DIBS pages.  However, once in DIBS, we do need
# to provide a way for them to un-authenticate themselves.  This is the
# reason for the asymmetry between /logout and (lack of) login.

@dibs.post('/logout')
def logout():
    '''Handle the logout action from the navbar menu on every page.'''
    # If we are not in debug mode, then whether the user is authenticated or
    # not is determined by the presence of REMOTE_USER.
    if request.environ.get('REMOTE_USER', None) and not debug_mode():
        redirect('/Shibboleth.sso/Logout')
    else:
        redirect('/')


@dibs.get('/list', apply = VerifyStaffUser())
def list_items():
    '''Display the list of known items.'''
    return page('list', browser_no_cache = True, items = Item.select(),
                manifest_dir = _MANIFEST_DIR, process_dir = _PROCESS_DIR)


@dibs.get('/manage', apply = VerifyStaffUser())
def manage_items():
    '''Manage the list of known items.'''
    return page('manage', browser_no_cache = True, items = Item.select())


@dibs.get('/add', apply = VerifyStaffUser())
def add_item():
    '''Display the page to add new items.'''
    return page('edit', action = 'add', item = None,
                thumbnails_dir = _THUMBNAILS_DIR,
                max_size = naturalsize(_MAX_THUMBNAIL_SIZE))


@dibs.get('/edit/<barcode:int>', apply = VerifyStaffUser())
def edit_item(barcode):
    '''Display the page to add new items.'''
    return page('edit', browser_no_cache = True, action = 'edit',
                thumbnails_dir = _THUMBNAILS_DIR,
                max_size = naturalsize(_MAX_THUMBNAIL_SIZE),
                item = Item.get(Item.barcode == barcode))


@dibs.post('/update/add', apply = VerifyStaffUser())
@dibs.post('/update/edit', apply = VerifyStaffUser())
def update_item():
    '''Handle http post request to add a new item from the add-new-item page.'''
    if 'cancel' in request.POST:
        log('user clicked Cancel button')
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
                    message = 'Duration must be a positive number')
    num_copies = request.forms.get('num_copies').strip()
    if not num_copies.isdigit() or int(num_copies) <= 0:
        return page('error', summary = 'invalid copy number',
                    message = '# of copies must be a positive number')
    notes = request.forms.get('notes').strip()
    thumbnail = request.files.get('thumbnail-image')

    item = Item.get_or_none(Item.barcode == barcode)
    if '/update/add' in request.path:
        if item:
            log(f'{barcode} already exists in the database')
            return page('error', summary = 'duplicate entry',
                        message = f'An item with barcode {barcode} already exists.')
        lsp = LSP()
        try:
            rec = lsp.record(barcode = barcode)
        except ValueError:
            return page('error', summary = 'Incomplete record in LSP',
                        message = (f'The item with barcode {barcode} lacks one'
                                   ' or more basic metadata fields (title,'
                                   ' author, year) in the library catalog.'))
        if not rec:
            log(f'could not find {barcode} in LSP')
            return page('error', summary = 'no such barcode',
                        message = f'Could not find an item with barcode {barcode}.')
        log(f'adding item entry {barcode} for {rec.title}')
        Item.create(barcode = barcode, title = rec.title, author = rec.author,
                    item_id = rec.id, item_page = rec.url, year = rec.year,
                    edition = rec.edition, publisher = rec.publisher,
                    num_copies = num_copies, duration = duration, notes = notes)
    else:  # The operation is /update/edit.
        if not item:
            log(f'there is no item with barcode {barcode}')
            return page('error', summary = 'no such barcode',
                        message = f'There is no item with barcode {barcode}.')
        item.barcode    = barcode
        item.duration   = duration
        item.num_copies = num_copies
        item.notes      = notes
        log(f'saving changes to {barcode}')
        item.save(only = [Item.barcode, Item.num_copies, Item.duration, Item.notes])
        # FIXME if we reduced the number of copies, we need to check loans.

        # Handle replacement thumbnail images if the user chose one.
        if thumbnail and thumbnail.filename:
            # We don't seem to get content-length in the headers, so won't know
            # the size ahead of time.  So, check size, & always convert to jpeg.
            try:
                data = b''
                while (chunk := thumbnail.file.read(1024)):
                    data += chunk
                    if len(data) >= _MAX_THUMBNAIL_SIZE:
                        max_size = naturalsize(_MAX_THUMBNAIL_SIZE)
                        log(f'file exceeds {max_size} -- ignoring the file')
                        return page('error', summary = 'cover image is too large',
                                    message = ('The chosen image is larger than'
                                               f' the limit of {max_size}.'))
                dest_file = join(_THUMBNAILS_DIR, barcode + '.jpg')
                log(f'writing {naturalsize(len(data))} image to {dest_file}')
                with open(dest_file, 'wb') as new_file:
                    new_file.write(as_jpeg(data))
            except Exception as ex:     # noqa: PIE786
                log(f'exception trying to save thumbnail: {str(ex)}')
        else:
            log('user did not provide a new thumbnail image file')
    redirect(f'{dibs.base_url}/list')


@dibs.get('/delete-thumbnail/<barcode:int>', apply = VerifyStaffUser())
def edit(barcode):
    '''Delete the current thumbnail image.'''
    thumbnail_file = join(_THUMBNAILS_DIR, str(barcode) + '.jpg')
    if exists(thumbnail_file):
        delete_existing(thumbnail_file)
    else:
        log(f'there is no {thumbnail_file}')
    redirect(f'{dibs.base_url}/edit/{barcode}')


@dibs.post('/start-processing', apply = VerifyStaffUser())
def start_processing():
    '''Handle http post request to start the processing workflow.'''
    barcode = request.POST.barcode.strip()
    if _PROCESS_DIR:
        init_file = join(_PROCESS_DIR, f'{barcode}-initiated')
        try:
            log(f'creating {init_file}')
            os.close(os.open(init_file, os.O_CREAT))
        except OSError as ex:
            log(f'problem creating {init_file}: {str(ex)}')
    else:
        log(f'_PROCESS_DIR not set -- ignoring /start-processing for {barcode}')
    redirect(f'{dibs.base_url}/list')


@dibs.post('/ready', apply = VerifyStaffUser())
def toggle_ready():
    '''Set the ready-to-loan field.'''
    barcode = request.POST.barcode.strip()
    item = Item.get(Item.barcode == barcode)
    item.ready = not item.ready
    log(f'locking db to change {barcode} ready to {item.ready}')
    with database.atomic('immediate'):
        item.save(only = [Item.ready])
        # If we are removing readiness, we may have to close outstanding
        # loans.  Doesn't matter if these are active or recent loans.
        if not item.ready:
            for loan in Loan.select().where(Loan.item == item):
                # Don't count staff users in loan stats except in debug mode.
                if staff_user(loan.user) and not debug_mode():
                    continue
                History.create(type = 'loan', what = barcode,
                               start_time = loan.start_time,
                               end_time = loan.end_time)
            n = Loan.delete().where(Loan.item == item).execute()
            if n > 0:
                log(f'deleted {n} loans for {barcode}')
    redirect(f'{dibs.base_url}/list')


@dibs.post('/remove', apply = VerifyStaffUser())
def remove_item():
    '''Handle http post request to remove an item from the database.'''
    barcode = request.POST.barcode.strip()
    item = Item.get(Item.barcode == barcode)
    log(f'locking db to remove {barcode}')
    with database.atomic('immediate'):
        item.ready = False
        item.save(only = [Item.ready])
        Loan.delete().where(Loan.item == item).execute()
        # Note we don't create History for items that will no longer exist.
        Item.delete().where(Item.barcode == barcode).execute()
    redirect(f'{dibs.base_url}/manage')


@dibs.get('/stats', apply = VerifyStaffUser())
@dibs.get('/status', apply = VerifyStaffUser())
def show_stats():
    '''Display the list of known items.'''
    usage_data = []
    for item in Item.select():
        barcode = item.barcode
        active = Loan.select().where(Loan.item == item, Loan.state == 'active').count()
        history = History.select().where(History.what == barcode, History.type == 'loan')
        last_15min = _REQUESTS['15'].get(barcode, 0)
        last_30min = _REQUESTS['30'].get(barcode, 0)
        last_45min = _REQUESTS['45'].get(barcode, 0)
        last_60min = _REQUESTS['60'].get(barcode, 0)
        retrievals = [last_15min ,
                      max(0, last_30min - last_15min),
                      max(0, last_45min - last_30min - last_15min),
                      max(0, last_60min - last_45min - last_30min - last_15min)]
        durations = [(loan.end_time - loan.start_time) for loan in history]
        if durations:
            avg_duration = sum(durations, delta()) // len(durations)
        else:
            avg_duration = delta(seconds = 0)
        usage_data.append((item, active, len(durations), avg_duration, retrievals))
    return page('stats', browser_no_cache = True, usage_data = usage_data)


@dibs.get('/download/<fmt:re:(csv|json)>/<data:re:(item|history)>', apply = VerifyStaffUser())
def download(fmt, data):
    '''Handle http post request to download data from the database.'''
    # The values of "data" are limited to known table names by the route, but
    # if data_models.py is ever changed and we forget to update this function,
    # the next safety check prevents db.freeze from creating a blank table.
    if data not in generate_models(database):
        log(f'download route database mismatch: requested {data} does not exist')
        return page('error', summary = f'unable to download {data} data',
                    message = 'The requested data is missing from the database ')
    db = DataSet('sqlite:///' + database.file_path)
    buffer = StringIO()
    db.freeze(db[data].all(), format = fmt, file_obj = buffer)
    buffer.seek(0)
    response = LocalResponse(
        body = buffer,
        headers = {
            'Content-Disposition' : f'attachment; filename=dibs-{data}',
            'Content-Type'        : f'text/{fmt}',
        })
    log(f'returning file "dibs-{data}.{fmt}" to user')
    return response


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
    who = anon(user)
    if loan:
        if loan.state == 'active':
            log(f'{who} already has {barcode} on loan')
            status = Status.LOANED_BY_USER
            explanation = 'This item is currently on digital loan to you.'
        else:
            log(f'{who} had a loan on {barcode} too recently')
            status = Status.TOO_SOON
            explanation = ('Your loan period has ended and it is too soon '
                           'after the last time you borrowed it.')
            when_available = loan.reloan_time
    else:
        loan = Loan.get_or_none(Loan.user == user, Loan.state == 'active')
        if loan:
            other = loan.item
            log(f'{who} has a loan on {other.barcode} that ends at {loan.end_time}')
            status = Status.USER_HAS_OTHER
            author = shorten(other.author, width = 50, placeholder = ' …')
            explanation = ('You have another item currently on loan'
                           f' ("{other.title}" by {author}).')
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
                log(f'{who} is allowed to borrow {barcode}')
                status = Status.AVAILABLE

    return item, status, explanation, when_available


@dibs.get('/')
@dibs.get('/<name:re:(info|about|thankyou)>')
def general_page(name = '/'):
    '''Display the welcome page.'''
    if name and name in ['info', 'about', 'thankyou']:
        return page(f'{name}')
    else:
        return page('info')


# Next one is used by the item page to update itself w/o reloading whole page.

@dibs.get('/item-status/<barcode:int>', apply = AddPersonArgument())
def item_status(barcode, person):
    '''Returns an item summary status as a JSON string'''
    item, status, explanation, when_available = loan_availability(person.uname, barcode)
    return json.dumps({'available'     : (status == Status.AVAILABLE),
                       'loaned_by_user': (status == Status.LOANED_BY_USER),
                       'explanation'   : explanation,
                       'when_available': human_datetime(when_available)})


@dibs.get('/item/<barcode:int>', apply = AddPersonArgument())
def show_item_info(barcode, person):
    '''Display information about the given item.'''
    item, status, explanation, when_available = loan_availability(person.uname, barcode)
    # Users can put ?viewer=0 to avoid being sent to the viewer if they have
    # the item on loan.  This is useful mainly for developers and staff.
    show_viewer = str2bool(request.query.get('viewer', '1'))
    if status == Status.LOANED_BY_USER and show_viewer:
        log(f'redirecting {user(person)} to uv for {barcode}')
        redirect(f'{dibs.base_url}/view/{barcode}')
        return
    return page('item', browser_no_cache = True, item = item,
                available = (status == Status.AVAILABLE),
                when_available = human_datetime(when_available),
                explanation = explanation, thumbnails_dir = _THUMBNAILS_DIR)


@dibs.post('/loan', apply = AddPersonArgument())
def loan_item(person):
    '''Handle http post request to loan out an item, from the item info page.'''
    barcode = request.POST.barcode.strip()
    # Checking if the item is available requires steps, and we have to be sure
    # that two users don't do them concurrently, or else we might make 2 loans.
    log('locking db')
    with database.atomic('immediate'):
        item, status, explanation, when_available = loan_availability(person.uname, barcode)
        if status == Status.NOT_READY:
            # Normally we shouldn't see a loan request through this form if the
            # item is not ready, so either staff changed the status after the
            # item was made available or someone got here accidentally.
            log(f'redirecting {user(person)} back to item page for {barcode}')
            redirect(f'{dibs.base_url}/item/{barcode}')
            return
        if status == Status.LOANED_BY_USER:
            # Shouldn't be able to reach this point b/c the item page
            # shouldn't make a loan available for this user & item combo.
            # But if something weird happens, we might.
            log(f'redirecting {user(person)} to {dibs.base_url}/view/{barcode}')
            redirect(f'{dibs.base_url}/view/{barcode}')
            return
        if status == Status.USER_HAS_OTHER:
            return page('error', summary = 'only one loan at a time',
                        message = ('Our policy currently prevents users from '
                                   'borrowing more than one item at a time.'))
        if status == Status.TOO_SOON:
            return page('error', summary = 'too soon',
                        message = ('We ask that you wait at least '
                                   f'{naturaldelta(_RELOAN_WAIT_TIME)} before '
                                   f'requesting the same item again. Please try '
                                   f'after {human_datetime(when_available)}'))
        if status == Status.NO_COPIES_LEFT:
            # The loan button shouldn't have been clickable in this case, but
            # someone else might have gotten the loan between the last status
            # check and the user clicking it.
            log(f'redirecting {user(person)} to {dibs.base_url}/view/{barcode}')
            redirect(f'{dibs.base_url}/view/{barcode}')
            return

        # OK, the user is allowed to loan out this item.  Round up the time to
        # the next minute to avoid loan times ending in the middle of a minute.
        time = delta(minutes = 1) if debug_mode() else delta(hours = item.duration)
        start = time_now()
        end = round_minutes(start + time, 'up')
        reloan = end + _RELOAN_WAIT_TIME
        log(f'creating new loan for {barcode} for {user(person)}')
        Loan.create(item = item, state = 'active', user = person.uname,
                    start_time = start, end_time = end, reloan_time = reloan)

    send_email(person.uname, item, start, end, dibs.base_url)
    log(f'redirecting {user(person)} to viewer page for new loan on {barcode}')
    redirect(f'{dibs.base_url}/view/{barcode}')


@dibs.post('/return/<barcode:int>', apply = AddPersonArgument())
def end_loan(barcode, person):
    '''Handle http post request to return the given item early.'''

    # Sometimes, for unknown reasons, the end-loan button sends a post without
    # the barcode data.  The following are compensatory mechanisms.
    post_barcode = request.POST.get('barcode')
    if not post_barcode:
        log(f'missing post barcode in /return by user {user(person)}')
        if barcode:
            log(f'using barcode {barcode} from post address instead')
        else:
            log(f'/return invoked by user {user(person)} but we have no barcode')
            return
    else:
        barcode = post_barcode

    item = Item.get(Item.barcode == barcode)
    loan = Loan.get_or_none(Loan.item == item, Loan.user == person.uname)
    if loan and loan.state == 'active':
        # Normal case: user has loaned a copy of item. Update to 'recent'.
        log(f'locking db to change {barcode} loan state by user {user(person)}')
        with database.atomic('immediate'):
            now = time_now()
            loan.state = 'recent'
            loan.end_time = now
            loan.reloan_time = round_minutes(now + _RELOAN_WAIT_TIME, 'down')
            loan.save(only = [Loan.state, Loan.end_time, Loan.reloan_time])
            if not staff_user(loan.user) or debug_mode():
                # Don't count staff users in loan stats except in debug mode.
                History.create(type = 'loan', what = loan.item.barcode,
                               start_time = loan.start_time,
                               end_time = loan.end_time)
        redirect(f'{dibs.base_url}/thankyou')
    else:
        log(f'{user(person)} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/item/{barcode}')


@dibs.get('/view/<barcode:int>', apply = AddPersonArgument())
def send_item_to_viewer(barcode, person):
    '''Redirect to the viewer.'''
    item = Item.get(Item.barcode == barcode)
    loan = Loan.get_or_none(Loan.item == item, Loan.user == person.uname)
    if loan and loan.state == 'active':
        log(f'redirecting to viewer for {barcode} for {user(person)}')
        wait_time = _RELOAN_WAIT_TIME
        return page('uv', browser_no_cache = True, barcode = barcode,
                    title = shorten(item.title, width = 100, placeholder = ' …'),
                    end_time = human_datetime(loan.end_time, '%I:%M %p (%b %d, %Z)'),
                    js_end_time = human_datetime(loan.end_time, '%m/%d/%Y %H:%M:%S'),
                    wait_time = naturaldelta(wait_time))
    else:
        log(f'{user(person)} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/item/{barcode}')


@dibs.get('/manifests/<barcode:int>', apply = AddPersonArgument())
def return_iiif_manifest(barcode, person):
    '''Return the manifest file for a given item.'''
    item = Item.get(Item.barcode == barcode)
    loan = Loan.get_or_none(Loan.item == item, Loan.user == person.uname)
    if loan and loan.state == 'active':
        manifest_file = join(_MANIFEST_DIR, f'{barcode}-manifest.json')
        if not exists(manifest_file):
            log(f'{manifest_file} does not exist')
            return
        record_request(barcode)
        with open(manifest_file, 'r', encoding = 'utf-8') as mf:
            adjusted_content = urls_rerouted(mf.read(), barcode)
            encoded_content = adjusted_content.encode()
            data = BytesIO(encoded_content)
            size = len(encoded_content)
            log(f'returning manifest for {barcode} for {user(person)}')
            return send_file(data, ctype = 'application/json', size = size)
    else:
        log(f'{user(person)} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/notallowed')
        return


@dibs.get('/iiif/<barcode>/<rest:re:.+>', apply = AddPersonArgument())
def return_iiif_content(barcode, rest, person):
    '''Return the manifest file for a given item.'''
    item = Item.get(Item.barcode == barcode)
    loan = Loan.get_or_none(Loan.item == item, Loan.user == person.uname)
    if loan and loan.state == 'active':
        record_request(barcode)
        url = _IIIF_BASE_URL + '/' + urls_restored(rest, barcode)
        if url in _IIIF_CACHE:
            content, ctype = _IIIF_CACHE[url]
            data = BytesIO(content)
            log(f'returning cached /iiif/{barcode}/{rest} for {user(person)}')
            return send_file(data, ctype = ctype, size = len(content))

        # Read the data from our IIIF server instance & send it to the client.
        log(f'getting /iiif/{barcode}/{rest} from server')
        response, error = net('get', url)
        if not error:
            if url.endswith('json'):
                # Always rewrite URLs in any JSON files we send to the client.
                content = urls_rerouted(response.text, barcode).encode()
                ctype = 'application/json'
            else:
                content = response.content
                ctype = 'image/jpeg'
            _IIIF_CACHE[url] = (content, ctype)
            data = BytesIO(content)
            log(f'returning content of /iiif/{barcode}/{rest} for {user(person)}')
            return send_file(data, ctype = ctype, size = len(content))
        else:
            log(f'error {str(error)} accessing {url}')
            return
    else:
        log(f'{user(person)} does not have {barcode} loaned out')
        redirect(f'{dibs.base_url}/notallowed')


# Universal viewer interface.
# .............................................................................
# The uv subdirectory contains generic html and css.  We serve them as static
# files to anyone; they don't need to be controlled.  The multiple routes
# are because the UV files themselves reference different paths.

_UNNECESSARY_PLUGINS = [
    DatabaseConnector, LoanExpirer, BarcodeVerifier, RouteTracer
]

@dibs.route('/view/uv/<filepath:path>', skip = _UNNECESSARY_PLUGINS)
@dibs.route('/viewer/uv/<filepath:path>', skip = _UNNECESSARY_PLUGINS)
def serve_uv_files(filepath):
    log(f'serving static uv file /viewer/uv/{filepath}')
    return static_file(filepath, root = 'viewer/uv')


@dibs.route('/view/img/<filepath:path>', skip = _UNNECESSARY_PLUGINS)
@dibs.route('/viewer/img/<filepath:path>', skip = _UNNECESSARY_PLUGINS)
def serve_uv_img_files(filepath):
    log(f'serving static uv file /viewer/img/{filepath}')
    return static_file(filepath, root = 'viewer/img')


@dibs.route('/view/lib/<filepath:path>', skip = _UNNECESSARY_PLUGINS)
@dibs.route('/viewer/lib/<filepath:path>', skip = _UNNECESSARY_PLUGINS)
def serve_uv_lib_files(filepath):
    # Don't return config files from UV because they would override ours.
    # Otherwise, return the requested file.
    if filepath.endswith('.config.json'):
        log('serving file /dibs/static/uv-config.json')
        return static_file('uv-config.json', root = 'dibs/static')
    else:
        log(f'serving static uv file /viewer/lib/{filepath}')
        return static_file(filepath, root = 'viewer/lib')


@dibs.route('/view/themes/<filepath:path>', skip = _UNNECESSARY_PLUGINS)
@dibs.route('/viewer/themes/<filepath:path>', skip = _UNNECESSARY_PLUGINS)
def serve_uv_themes_files(filepath):
    # Intercept requests for undefined themes and reroute them to a default.
    if filepath.startswith('undefined'):
        filepath = filepath.replace('undefined', 'uv-en-gb-theme')
    log(f'serving static uv file /viewer/themes/{filepath}')
    return static_file(filepath, root = 'viewer/themes')


@dibs.route('/viewer/<filepath:path>', skip = _UNNECESSARY_PLUGINS)
def serve_viewer_files(filepath):
    log(f'serving static uv file /viewer/{filepath}')
    return static_file(filepath, root = 'viewer')


# Error pages.
# .............................................................................
# Note: the Bottle session plugin does not seem to supply session arg to @error.

@dibs.get('/notallowed')
@dibs.post('/notallowed')
def not_allowed():
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


# Miscellaneous static pages and files.
# .............................................................................

@dibs.get('/favicon.ico', skip = _UNNECESSARY_PLUGINS)
def favicon():
    '''Return the favicon.'''
    return static_file('favicon.ico', root = 'dibs/static')


@dibs.get('/thumbnails/<filename:re:[0-9]+.jpg>', skip = _UNNECESSARY_PLUGINS)
def thumbnail_file(filename):
    '''Return a thumbnail image file.'''
    log(f'returning included file {filename}')
    return static_file(filename, root = _THUMBNAILS_DIR)


@dibs.get('/static/<filename:re:[-a-zA-Z0-9]+.(html|jpg|svg|css|js|json)>',
          skip = _UNNECESSARY_PLUGINS)
def included_file(filename):
    '''Return a static file used with %include in a template.'''
    log(f'returning included file {filename}')
    return static_file(filename, root = 'dibs/static')
