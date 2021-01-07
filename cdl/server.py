from   decouple import config
import bottle
from   bottle import route, run, template
from   bottle import get, post, request
from   peewee import *
from   os import path

from .database import Item


# Service endpoints.
# .............................................................................

@get('/list') # or @route('/view')
def list_items():
    return template(path.join(config('TEMPLATE_DIR'), 'list'),
                    items = Item.select())


# Server runner.
# .............................................................................

class Server():
    def __init__(self, host = 'localhost', port = 8080, debug = True):
        self.host = host
        self.port = port
        self.debug = debug


    def run(self):
        bottle.debug(self.debug)
        bottle.run(reloader = True, host = self.host, port = self.port)
