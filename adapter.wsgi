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
from   os.path import realpath, dirname
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

# Notes:
#
# 1) We set a variable on "dibs" (the application object), named "base_url",
# in the function dibs_application() below.  Our application code in
# dibs/server.py relies on it.  It's done as a one-time setting.
#
# 2) Mod_wsgi runs this .wsgi adapter with a clean environment; you cannot pass
# arguments to this wrapper. Mod_wsgi expects tha you use a separate config
# file or alternative .wsgi scripts for different run-time configurations.
# That's okay, but it makes it difficult if you want to keep things simple
# and not use multiple adapter files.  So, the approach taken here is to have
# dibs_application(...) do a one-time operation to look for environment
# variables and/or settings.ini values that change some behaviors.  It sets a
# flag and skips that step on subsequent invocations.  This allows us to do
# some configurations based on environment variables and settings.ini files
# (instead of having different .wsgi files for different configurations), yet
# avoid the inefficiency of doing that at every invocation.  Our "run-server"
# script takes advantage of that: it uses mod_wsgi-express's ability to set
# environment variables, and sets DEBUG or VERBOSE if the user requests it.

dibs._config_done = False

def dibs_application(env, start_response):
    '''DIBS wrapper around Bottle WSGI application.'''
    if not dibs._config_done:
        if 'VERBOSE' in env:
            set_debug(True, '-', show_package = True)
            log('VERBOSE found in env')

        # DEBUG in env overrides settings.ini, hence test it first.
        if 'DEBUG' in env or config('DEBUG', cast = bool, default = False):
            set_debug(True, '-', show_package = True)
            bottle.debug(True)
            dibs.catchall = False       # Make Bottle go into pdb on exceptions
            log('DEBUG is True -- running on debug mode')

        # Determine our base url and set it once. No sense in computing this
        # on every call, because it won't change while running.  Set a custom
        # property on the dibs Bottle object so our server code can read it.
        if 'SERVER_NAME' not in env or env['SERVER_NAME'] == '':
            raise ValueError('SERVER_NAME not set in WSGI environment')
        host = env['SERVER_NAME']
        if 'wsgi.url_scheme' in env and env["wsgi.url_scheme"] != '':
            url = f'{env["wsgi.url_scheme"]}://{host}'
        elif 'REQUEST_SCHEME' in env and env["REQUEST_SCHEME"] != '':
            url = f'{env["REQUEST_SCHEME"]}://{host}'
        elif 'SERVER_PORT' in env and env['SERVER_PORT'] == '443':
            url = f'https://{host}'
        else:
            url = f'http://{host}'
        if ('SERVER_PORT' in env and env['SERVER_PORT'] != ''
            and env['SERVER_PORT'] not in ['80', '443']):
            url = f'{url}:{env["SERVER_PORT"]}'
        if 'SCRIPT_NAME' in env:
            url = f'{url}{env["SCRIPT_NAME"]}'
        dibs.base_url = url
        log(f'dibs.base_url = {url}')

        # Mark this done.
        dibs._config_done = True

    # Now call the real DIBS Bottle server to process the request.
    return dibs(env, start_response)


# Hook in the default WSGI interface application.  Mod_wsgi looks for a
# variable named 'application' unless told otherwise.

application = dibs_application
