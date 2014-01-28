from lib import bottle
from lib import pyrrdtool as rrd
import config

import os, errno

# Bottle application
app = bottle.app()

# Loads and mounts api app
# FIXME: Mounted routes issue with app.get_url()
#        The response object within mounted app does has no effect
#        - try app.load_app() ?
#from api import api
#app.mount("/api/", bottle.load_app('api.api:app'))

# Makes get_url available to templates
bottle.BaseTemplate.defaults['get_url'] = app.get_url

# API methods
@app.route('/')
def home():
    #FIXME: redirects to web page for dev/demo purpose
    bottle.redirect(app.get_url('rrd-view'))
    return {'FIXME': 'List available entry points and __doc__'}

@app.route('/rrd')
def rrd_list():
    "Lists all available RRDs"
    files = next(os.walk(config.rrd_basepath))[2]
    return {
        'path': config.rrd_basepath,
        'files': files,
        'urls': [app.get_url('rrd-info', filename=file) for file in files]
    }

@app.route('/rrd/info/<filename>', name='rrd-info')
def rrd_info(filename):
    "Shows RRD info data"
    return {
        'info': rrd.info(os.path.join(config.rrd_basepath, filename))
    }

@app.route('/rrd/fetch/<filename>', name='rrd-fetch')
def rrd_fetch(filename, limit=50):
    "Lists RRDs data rows"
    limit = int(bottle.request.params.get('limit', limit))
    data = rrd.RRD.load(os.path.join(config.rrd_basepath, filename)).fetch()
    return {
        'count': len(data),
        'limit': limit,
        'data': data[:limit]
    }

@app.route('/rrd/graph/<filename>', name='rrd-graph')
def rrd_graph(filename):
    "Returns a graph binary from the given filename"
    #FIXME: allow graph options in query-string
    args = dict({
        'border': '0'
    }.items() + bottle.request.params.items())
    #FIXME: dynamic mime-type according rrdtool imgformat
    db = rrd.RRD.load(os.path.join(config.rrd_basepath, filename))
    data = [rrd.DEF.from_variable(rrd.Variable(db, ds.name))
            for ds in db.datasources]
    style = [rrd.LINE.from_variable(variable, {'color':'555555'})
             for variable in data]
    # Response contents
    bottle.response.set_header('Content-Type', 'image/png')
    return rrd.Graph(data, style, args=args).draw()

@app.route('/rrd/igraph/<filename>', name='rrd-igraph')
@bottle.view('igraph')
def rrd_igraph(filename):
    #FIXME: modularize jquery-zoomly to allow multiple connectors (smokeping, rrdli)
    return {'url': app.get_url('rrd-graph', filename=filename)}

# View methods (fix route)
@app.route('/view', name='rrd-view')
def view_rrd_list():
    # Returns HTML of rrd list and urls
    rrds = [{'filename': filename,
             'info': app.get_url('rrd-info', filename=filename),
             'fetch': app.get_url('rrd-fetch', filename=filename),
             'graph': app.get_url('rrd-graph', filename=filename)}
             #'scroll': app.get_url('rrd-scroll', filename=filename)}
                 for filename in sorted(rrd_list().get('files')) or []]
    return bottle.template('views/rrd-list', rrds=rrds)

@app.route('/static/<file:path>', name='static')
def static(file):
    return bottle.static_file(file, root='')

@bottle.error(500)
def error(error):
    import json
    return json.dumps({'error': error.exception.message})

# Setup logic
def setup():
    # Ensures rrd container path exists
    path = config.rrd_basepath
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path): pass
        else: raise

setup()
