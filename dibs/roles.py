'''
roles.py uses a DICT to map a role string to a redirect destination. The
function role_to_redirect(...) provides a safe encapsulation, as the role
application will likely evolve over time.

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from .database import Person


_role_table = {
    "library": "list",
}

def has_role(person, role):
    if (person == None):
        return False
    return person.has_role(role)


def role_to_redirect(role):
    '''Given a user role (including an empty string), return the target
    path for a redirect.'''
    if role in _role_table:
        return _role_table[role]
    else:
        return ''


def staff_user(who):
    '''Return True if the person has admin priviledges in the system.'''
    if isinstance(who, str):
        # Given a user name -- look them up and try to retrieve a Person object.
        who = Person.get_or_none(Person.uname == who)
    return has_role(who, 'library')
