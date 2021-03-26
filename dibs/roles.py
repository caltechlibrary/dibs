'''
roles.py provides a DICT that maps a role string to a target
redirect. The function role_to_redirect provides a safe encapsulation
as the role application will likely evolve over time.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from sidetrack import log

_role_table = {
    "library": "list",
}

def has_required_role(person, required_role):
    if (person == None):
        return False
    log(f'person type: {type(person)}')
    return person.has_role(required_role)

def role_to_redirect(role):
    '''given a user role (including an empty string) return the target path for a redirect'''
    if role in _role_table:
        return _role_table[role]
    else:
        return ''

