'''
people.py provides account profiles for a persons based on their fields
in the Person table in an SQLite3 database.

It does not provide suppport for authentication, that needs to be
provided by your front end web server such as Apache 2. If you
have Apache2's Basic Auth the PersonManager class will attempt
to store/update/remove passwords (aka secrets) via the
Apache htpasswd program.

No password are stored in the SQLite3 person table.

Copyright
---------

Copyright (c) 2021-2022 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from datetime import datetime
from getpass import getpass
from peewee import SqliteDatabase
from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.table import Table
from subprocess import Popen, PIPE

import os
import sys

from .data_models import Person
from .date_utils import human_datetime


def setup_person_table(db_name):
    '''setup a people SQLite3 database'''
    db = SqliteDatabase(db_name)
    if db.connect():
        if db.table_exists('person'):
            print(f'WARNING: person already exists in {db_name}')
        else:
            db.create_tables([Person])
    else:
        print(f'ERROR: could not connect to {db_name}')


# GuestPerson only exists while REMOTE_USER available in the environment.
# It is not stored in the person table as the Person model is.
class GuestPerson():
    '''GuestPerson is an object for non-staff people.  It has the same
    signature but is not persisted in the person table of the database.
    '''
    def __init__(self, uname = '', display_name = '', role = ''):
        self.uname = uname                # user name, e.g. janedoe
        self.display_name = display_name  # display_name, optional
        self.role = role                  # role is empty or "staff"
        self.updated = datetime.now()

    def has_role(self, required_role):
        return self.role == required_role


def person_from_environ(environ):
    if 'REMOTE_USER' in environ:
        # NOTE: If we're shibbed then we always return a Person object.
        # Either they are a known person (e.g. library staff) or other community
        # member without a role.
        person = Person.get_or_none(Person.uname == environ['REMOTE_USER'])
        if person is None:
            person = GuestPerson()
            person.uname = environ['REMOTE_USER']
            person.display_name = environ['REMOTE_USER']
        return person
    else:
        return None


def normalize_str(s):
    if isinstance(s, bytes):
        return s.decode('utf-8')
    return s


# NOTE: The following are used by people-manager and are not expected
# to be used in the web UI.
#
class PersonManager:
    '''PersonManager provides a class to build a CLI person manager.'''
    def __init__(self, db_name, htpasswd = None, password_file = None):
        self.htpasswd = htpasswd
        self.password_file = password_file
        self.db_name = db_name

    def _update_htpasswd(self, uname, secret):
        '''Update the password for user using htpasswd from Apache.'''
        if (self.htpasswd is None) or (self.password_file is None):
            print('ERROR: not set up for Apache htpasswd support')
            sys.exit(1)
        if not os.path.exists(self.password_file):
            print(f'ERROR: password file {self.password_file} does not exist')
            sys.exit(1)
        if not secret:
            secret = getpass(prompt='Password: ', stream = None)
        if not secret:
            return False
        cmd = [self.htpasswd, '-b', self.password_file, uname, secret]
        with Popen(cmd, stdout = PIPE, stderr = PIPE) as proc:
            out = normalize_str(proc.stdout.read())
            err = normalize_str(proc.stderr.read())
            if out:
                print(out)
            if err:
                print(err)
        return True

    def _delete_htpasswd(self, uname):
        if (self.htpasswd is None) or (self.password_file is None):
            print('ERROR: not setup for Apache htpasswd support')
            sys.exit(1)
        if not os.path.exists(self.password_file):
            print(f'ERROR: password file {self.password_file} does not exist')
            sys.exit(1)
        cmd = [self.htpasswd, '-D', self.password_file, uname]
        with Popen(cmd, stdout = PIPE, stderr = PIPE) as proc:
            out = normalize_str(proc.stdout.read())
            err = normalize_str(proc.stderr.read())
            if out:
                print(out)
            if err:
                print(err)
        return True

    def add_people(self, kv):
        if 'uname' not in kv:
            print('ERROR: uname is required')
            sys.exit(1)
        if ('secret' in kv):
            if self.htpasswd is not None:
                self._update_htpasswd(kv['uname'], kv['secret'])
            else:
                print('WARNING: secrets not supported')
        for key in ['role', 'display_name']:
            if key not in kv:
                kv[key] = ''
        user = Person(uname = kv['uname'], role = kv['role'], display_name = kv['display_name'])
        user.save()

    def update_people(self, kv):
        user = Person.select().where(Person.uname == kv['uname']).get()
        if user is None:
            print(f'ERROR {kv["uname"]} does not exist')
            sys.exit(1)
        if ('secret' in kv):
            if self.htpasswd is not None:
                self._update_htpasswd(user.uname, kv['secret'])
            else:
                print('WARNING: secrets not supported')
        if 'display_name' in kv:
            user.display_name = kv['display_name']
        if 'role' in kv:
            user.role = kv['role']
        user.save()

    def remove_people(self, kv):
        if 'uname' not in kv:
            print('WARNING: uname is required')
            sys.exit(1)
        nrows = Person.delete().where(Person.uname == kv['uname']).execute()
        if self.htpasswd is not None:
            self._delete_htpasswd(kv['uname'])
        print(f'{nrows} row deleted from person in {self.db_name}')

    def list_people(self, kv):
        '''List people in the SQLite3 database table called person.'''
        table = Table(pad_edge = False, box = box.MINIMAL_DOUBLE_HEAD)
        table.add_column('User name', style = 'sky_blue2')
        table.add_column('Display name', style = 'medium_turquoise')
        table.add_column('Role')
        table.add_column('updated', style = 'light_cyan3')
        if 'uname' in kv:
            row = (Person.select().where(Person.uname == kv['uname']).get())
            if row:
                updated = human_datetime(row.updated)
                table.add_row(row.uname, row.display_name, row.role, updated)
            else:
                table.add_row(kv['uname'], 'n/a', 'n/a', 'n/a')
        else:
            query = (Person.select().order_by(Person.display_name))
            for row in query:
                updated = human_datetime(row.updated)
                table.add_row(row.uname, row.display_name, row.role, updated)
        console = Console()
        console.print(Padding('[white italic]List of people in database[/]', (1, 0, 0, 1)))
        console.print(table)
