'''
roles.py provides a DICT that maps a role string to a target
redirect. The function role_to_redirect provides a safe encapsulation
as the role application will likely evolve over time.
'''


_role_table = {
    "library": "/list",
}


def role_to_redirect(role, base_url = 'http://localhost:8080'):
    '''given a user role (including an empty string) return the target path for a redirect'''
    if role in _role_table:
        return ''.join([base_url, _role_table[role]])
    else:
        return ''.join([base_url, '/'])

