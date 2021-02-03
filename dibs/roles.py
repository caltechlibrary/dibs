'''
roles.py provides a DICT that maps a role string to a target
redirect. The function role_to_redirect provides a safe encapsulation
as the role application will likely evolve over time.
'''


_role_table = {
    "library": "/list",
}


def role_to_redirect(role):
    '''given a user role (including an empty string) return the target path for a redirect'''
    if role in _role_table:
        return _role_table[role]
    else:
        return '/'

