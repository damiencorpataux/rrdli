from lib import bottle
import api

# FIXME: App wrapper aims at providing an url prefix to the main app
# App wrapper
#wrapper = bottle.app()
#wrapper.mount('/api/', bottle.load_app('app:app'))

# Server instance
#bottle.run(api.app, host='0.0.0.0', port=8000, reloader=True, debug=True)
import paste
from paste import httpserver
bottle.run(server='paste', host='0.0.0.0', port='8000')
