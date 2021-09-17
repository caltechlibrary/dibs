'''
settings.py: interface for parsing the configuration file

This implements a subclass of Decouple's AutoConfig object which accepts a
parameter for a section name, such that values in a settings.ini file are
looked up within that section instead of Decouple's default "settings" section.
In addition, the "config" object provides a property, config_file, that holds
the path to the settings file being used by config.  Neither of these
capabilities exist in Decouple, but we needed them in DIBS.

This module provides a "config" object in the same way that Decouple provides
a "config" object.  Its class is DIBSAutoConfig instead of AutoConfig.

For more information about Python Decouple, see the repository at
https://github.com/henriquebastos/python-decouple

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   collections import OrderedDict
from   configparser import ConfigParser
from   decouple import Config, AutoConfig, DEFAULT_ENCODING, Undefined, undefined
from   decouple import RepositoryIni, RepositoryEnv, RepositoryEmpty
from   decouple import UndefinedValueError
import os
from   sidetrack import log


# Replacements for decouple classes.
# .............................................................................
# This is the minimum set of classes that has to be redefined in order to be
# able to add a 'section' keyword argument to the initializers.

class DIBSRepositoryIni(RepositoryIni):
    '''Subclass of decouple's RepositoryIni that accepts a section name.

    The default section name is "dibs".  It falls back to lookin for a
    section named "settings" (the default in Decouple) if no section name
    is given.
    '''

    def __init__(self, source, encoding = DEFAULT_ENCODING, section = 'dibs'):
        super().__init__(source, encoding)
        self.section = section
        self.parser = ConfigParser()
        log(f'reading ini file {source}')
        with open(source, encoding = encoding) as file_:
            self.parser.readfp(file_)


    def __contains__(self, key):
        return (key in os.environ
                or key in self.parser.sections()
                or ('settings' in self.parser.sections() and
                    self.parser.has_option('settings', key))
                or self.parser.has_option(self.section, key))


    def __getitem__(self, key):
        if key in self.parser.sections():
            return self.parser[key]
        elif self.parser.has_option(self.section, key):
            return self.parser.get(self.section, key)
        elif 'settings' in self.parser.sections():
            # If it fails this default case, let it throw an exception.
            return self.parser.get('settings', key)


class DIBSConfig(Config):
    def __init__(self, repository, section = 'dibs'):
        self.repository = repository
        self.section = section


    def get(self, option, default = undefined, cast = undefined, section = 'dibs'):
        '''Return the value for option or default if defined.'''
        # We can't avoid __contains__ because value may be empty.
        if isinstance(section, Undefined):
            section = self.section
        if option in os.environ:
            value = os.environ[option]
        elif section != undefined and section + '.' + option in os.environ:
            value = os.environ[section + '.' + option]
        elif option in self.repository:
            value = self.repository[option]
        elif section != undefined and section in self.repository.parser.sections():
            if self.repository.parser.has_option(section, option):
                value = self.repository[section][option]
            elif not isinstance(default, Undefined):
                value = default
            else:
                msg = f'Setting variable {option} not found in section [{section}].'
                raise UndefinedValueError(msg)
        else:
            if isinstance(default, Undefined):
                msg = f'Setting variable {option} not found in section [settings].'
                raise UndefinedValueError(msg)
            value = default

        if isinstance(cast, Undefined):
            cast = self._cast_do_nothing
        elif cast is bool:
            cast = self._cast_boolean

        return cast(value)


    def __call__(self, *args, **kwargs):
        """
        Convenient shortcut to get.
        """
        return self.get(*args, **kwargs)


class DIBSAutoConfig(AutoConfig):
    '''Subclass of decouple's AutoConfig that uses DIBSRepositoryIni.

    The property "config_file" on this object can be used to find out the
    path to the file from where it is reading its values.
    '''

    SUPPORTED = OrderedDict([
        ('settings.ini', DIBSRepositoryIni),
        ('.env', RepositoryEnv),
    ])

    def _load(self, path):
        # Avoid unintended permission errors
        try:
            filename = self._find_file(os.path.abspath(path))
        except Exception:
            filename = ''
        Repository = self.SUPPORTED.get(os.path.basename(filename), RepositoryEmpty)
        self.config = DIBSConfig(Repository(filename, encoding = self.encoding))
        self.config_file = filename


# Main exported symbol
# .............................................................................
# This is what users of this modules actually use.  In decouple, this is set
# to decouple's AutoConfig.

config = DIBSAutoConfig()
