from   decouple import config
import bottle
from   bottle import route, run, template, request
from   bottle import get, post, request, redirect, response
from   peewee import *
from   os import path

from .database import Item


# Service endpoints.
# .............................................................................

@get('/list') # or @route('/view')
def list_items():
    return template(path.join(config('TEMPLATE_DIR'), 'list'),
                    items = Item.select())


@get('/add')
def add():
    return template(path.join(config('TEMPLATE_DIR'), 'add'))


@post('/add')
def add_item():
    barcode = request.POST.inputBarcode.strip()
    title = request.POST.inputTitle.strip()
    author = request.POST.inputAuthor.strip()
    copies = request.POST.inputCopies.strip()
    tind_id = request.POST.inputTindId.strip()

    new_item = Item.create(barcode = barcode, title = title, author = author,
                           tind_id = tind_id, num_copies = copies)


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
