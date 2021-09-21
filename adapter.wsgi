# =============================================================================
# @file    adapter.wsgi
# @brief   WSGI adapter for DIBS
# @created 2021-02-01
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/dibs
# =============================================================================

# Initial imports. More things are imported later below.

import bottle
from   os import chdir
from   os.path import realpath, dirname
from   sidetrack import log, set_debug
import sys
from   werkzeug.wsgi import get_host, get_script_name

# The following sets the default directory to the current app's directory, so
# that imports and calls to config(...) work as expected.  It also prevents a
# confusing error of the form "FileNotFoundError: No such file or directory:
# '...../adapter.wsgi'" in the Apache or mod_wsgi logs.

app_directory = realpath(dirname(__file__))
sys.path.insert(0, app_directory)
chdir(app_directory)

# Now we can import our code.

from dibs.server import dibs, preflight_check
from dibs.settings import config

# Notes:
#
# 1) In the function dibs_application() below, we set variable "base_url" on
# "dibs" (our application object).  Our application code in dibs/server.py
# relies on this being set.  It's set only once.
#
# 2) Mod_wsgi runs this .wsgi adapter with a clean environment; you cannot pass
# arguments to this wrapper. Mod_wsgi expects that you use a separate config
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
# environment variables, and sets debug & verbose options if requested.
#
# 3) Keep in mind that mod_wsgi will normally run multiple processes and/or
# multiple threads (depending on the server configuration), which means this
# module (adapter.wsgi) will be invoked multiple times.

dibs._config_done = False

def dibs_application(env, start_response):
    '''DIBS wrapper around Bottle WSGI application.'''
    if not dibs._config_done:
        # VERBOSE in env overrides RUN_MODE which overrides settings.ini.
        mode = env.get('RUN_MODE', '') or config('RUN_MODE', default = 'normal')
        if env.get('VERBOSE', False) or mode == 'verbose':
            set_debug(True, '-', show_package = True)
            log('VERBOSE found in env')

        # Determine our base url and set it once. No sense in computing this
        # on every call, because it won't change while running.  Set a custom
        # property on the dibs Bottle object so our server code can read it.
        scheme = env.get('wsgi.url_scheme', '') or env.get('REQUEST_SCHEME', '')
        host   = get_host(env)
        path   = get_script_name(env)
        dibs.base_url = f'{scheme}://{host}{path}'
        log(f'dibs.base_url = {dibs.base_url}')

        # Make sure crucial directories are writable and variables are set.
        preflight_check()

        # Mark this done.
        dibs._config_done = True

    # Now call the real DIBS Bottle server to process the request.
    return dibs(env, start_response)


# Hook in the default WSGI interface application.  Mod_wsgi looks for a
# variable named 'application' unless told otherwise.

application = dibs_application
