# =============================================================================
# @file    adapter.wsgi
# @brief   WSGI adapter for DIBS
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/dibs
# =============================================================================

# Initial imports. More things are imported later below.

import bottle
from   decouple import config
from   os import chdir
from   os.path import exists, join, realpath, dirname
from   sidetrack import log, set_debug
import sys

# The following sets the default directory to the current app's directory, so
# that imports and calls to config(...) work as expected.  It also prevents a
# confusing error of the form "FileNotFoundError: No such file or directory:
# '...../adapter.wsgi'" in the Apache or mod_wsgi logs.

app_directory = realpath(dirname(__file__))
sys.path.insert(0, app_directory)
chdir(app_directory)

# Now we can import our code.

from dibs import dibs

# Mod_wsgi runs this .wsgi adapter with a clean environment; you cannot pass
# arguments to this wrapper, nor set environment variables in os.environ in
# the calling code and then read them here.  Mod_wsgi expects tha you use a
# separate config file or alternative .wsgi scripts for different run-time
# configurations.  That's okay, but it makes it difficult if you want to keep
# things simple and not use multiple adapter files.  So, the approach taken
# here is the following:
#
#  1. dibs_application(...) does a one-time operation to look for environment
#     variables and/or settings.ini values.  It sets a flag and skips the
#     operation on subsequent invocations.
#
#  2. Our run-server control script sets environment variables if the verbose
#     or debug options are given. That's what dibs_application(...) checks for.
#
# Note that THIS ENTRY POINT IS CALLED EVERY TIME a request comes in, for any
# page.  For efficiency, the following code is a bit roundabout but it's to
# avoid things like calling config() every time.

dibs._config_done = False

def dibs_application(env, start_response):
    '''DIBS wrapper around Bottle WSGI application.'''
    if not dibs._config_done:
        if 'VERBOSE' in env:
            set_debug(True, '-', show_package = True)
            log('VERBOSE found in env')

        # DEBUG in env overrides settings.ini.
        if 'DEBUG' in env:
            # Passed via setenv by run-server or Apache conf file.
            set_debug(True, '-', show_package = True)
            bottle.debug(True)
            log('DEBUG found in env')
            log('setting bottle.debug to True')
        elif config('DEBUG', cast = bool, default = False):
            # Value in settings.ini file is True.
            set_debug(True, '-', show_package = True)
            bottle.debug(True)
            log('DEBUG set true in settings.ini')

        # Determine our base url and set it once. No sense it computing this
        # on every call, because it won't change while running.  Set a custom
        # property on the dibs Bottle object so our server code can read it.
        if 'SERVER_NAME' not in env or env['SERVER_NAME'] == '':
            raise ValueError('SERVER_NAME not set in WSGI environment')
        host = env['SERVER_NAME']
        if 'wsgi.url_scheme' in env:
            url = f'{env["wsgi.url_scheme"]}://{host}'
        elif 'REQUEST_SCHEME' in env:
            url = f'{env["REQUEST_SCHEME"]}://{host}'
        elif 'SERVER_PORT' in env and env['SERVER_PORT'] == '443':
            url = f'https://{host}'
        else:
            url = f'http://{host}'
        if 'SERVER_PORT' in env and env['SERVER_PORT'] not in ['80', '443']:
            url = f'{url}:{env["SERVER_PORT"]}'
        if 'SCRIPT_NAME' in env:
            url = f'{url}/{env["SCRIPT_NAME"]}'
        log(f'setting our base_url to {url}')
        dibs.base_url = url

        # Mark this done.
        dibs._config_done = True

    # Now call the real DIBS Bottle server to process the request.
    return dibs(env, start_response)


# Hook in the default WSGI interface application.  Mod_wsgi looks for a
# variable named 'application' unless told otherwise.

application = dibs_application
