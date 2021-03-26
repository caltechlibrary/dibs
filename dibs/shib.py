'''
shib.py provides some quick routines to determine if the application
is running behind Shibboleth or not.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from bottle import request

def _val_set(environ, key):
    if (key in environ) and (environ[key] != None) and (environ[key] != ''):
        return True
    return False

def is_shibbed():
    env = request.environ
    if _val_set(env, "Shib-Session-ID") and _val_set(env, "Shib-Identity-Provider") and \
       _val_set(env, "Shib-Handler") and _val_set(env, 'REMOTE_USER'):
        return True
    return False

