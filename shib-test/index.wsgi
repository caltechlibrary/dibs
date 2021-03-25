#
# This is a simple WSGI bottle app for testing our Shibboleth setup.
# It privides a minimal set of options
#
# + /hello is a helloworld page
# + /whoami shows how REMOTE_USER is set
# + /env shows the full environment passed 
# + /logout shows an example of how you may want to handle logging out
#
import json

from bottle import Bottle, route, request, redirect

app = Bottle()

@app.route('/logout')
def logout():
	redirect("/Shibboleth.sso/Logout")

@app.route('/hello')
def hello():
    return 'Hello World'

@app.route('/whoami')
def whoami():
	environ = request.environ
	who = "Don't know"
	if 'REMOTE_USER' in environ:
		who = environ['REMOTE_USER']
	return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Shibboleth Test -- Who am I</title>
</head>
<body>
Who are you? {who}
</body>
</html>
'''

@app.route('/env')
def env():
    environ = request.environ
    env = {}
    for key in environ:
        if isinstance(environ[key], int):
            env[key] = f'{environ[key]}'
        elif isinstance(environ[key], str):
            env[key] = environ[key]
        elif isinstance(environ[key], tuple):
            env[key] = json.dumps(environ[key])
        else:
            env[key] = f'{type(environ[key])}'
                
    src = json.dumps(env, indent = 4)
    page = f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8" />
<title>Shib Test -- Environment</title>
</head>
<body>
<h1>Environment Variables</h1>
<code><pre>
{src}
</pre></code>
</body>
</html>
'''
    return page

@app.route('/')
@app.route('/index.html')
def default():
    return '''<DOCTYPE html>
<html>
<body>
<ul>
<li><a href="/secure/hello">Hello World</a></li>
<li><a href="/secure/whoami">Who am I?</a></li>
<li><a href="/secure/env">Environment</a></li>
<li><a href="/secure/logout">Logout</a></li>
</ul>
</body>
</html>
'''

application = app
