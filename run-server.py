from   peewee import *
import bottle
from   bottle import route, run, template
from   bottle import get, post, request

from   cdl.server import Server

server = Server(host = 'localhost', port = 8080)
server.run()
