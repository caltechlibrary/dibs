import os
import sys

from   decouple import config

app_directory = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, app_directory)
os.chdir(app_directory)

import bottle
bottle.TEMPLATE_PATH.insert(0, app_directory)

from dibs.server import server_config

server_config.set_base_url(config('BASE_URL'))

from bottle import route

@route('/testme')
def testme():
    return f'''The driod is in '{sys.path}'. Base URL: {server_config.get_base_url()}'''

application = bottle.default_app()

