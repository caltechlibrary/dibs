import os
import sys

app_directory = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, app_directory)
os.chdir(app_directory)

import bottle
bottle.TEMPLATE_PATH.insert(0, app_directory)

from dibs.server import *

from bottle import route

@route('/testme')
def testme():
    return f'''The driod is in '{sys.path}'.'''

application = bottle.default_app()

