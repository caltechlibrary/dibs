'''
settings.py: interface for parsing the configuration file

Copyright
---------

Copyright (c) 2021 by the California Institute of Technology.  This code
is open-source software released under a 3-clause BSD license.  Please see the
file "LICENSE" for more information.
'''

from   collections import OrderedDict
from   configparser import ConfigParser
from   decouple import config, AutoConfig
from   decouple import RepositoryIni, RepositoryEnv, DEFAULT_ENCODING
import os
from   sidetrack import log


class DIBSRepositoryIni(RepositoryIni):
    '''Subclass of decouple's RepositoryIni that accepts a section name.'''

    def __init__(self, source, encoding = DEFAULT_ENCODING, section = 'dibs'):
        super().__init__(source, encoding)
        self.section = section
        self.parser = ConfigParser()
        log(f'reading ini file {source}')
        with open(source, encoding = encoding) as file_:
            self.parser.readfp(file_)


    def __contains__(self, key):
        return (key in os.environ or self.parser.has_option(self.section, key))


    def __getitem__(self, key):
        return self.parser.get(self.section, key)


class DIBSConfig(AutoConfig):
    '''Subclass of decouple's AutoConfig that uses DIBSRepositoryIni.'''

    SUPPORTED = OrderedDict([
        ('settings.ini', DIBSRepositoryIni),
        ('.env', RepositoryEnv),
    ])


    def __init__(self, search_path = None):
        log(f'initializing DIBSConfig with search_path = {search_path}')
        super().__init__(search_path)


config = DIBSConfig()
