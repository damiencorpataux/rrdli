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

#FIXME: is it a good idea to include start/end in url ?
#       it helps caching past graphs, but caching current or future
#       timespan graphs is not what we want (data will be missing then)
#       note that rrd_graph could check if the served graph contains future
#       and set Cache-Control headers accordingly.
#@app.route('/rrd/graph/<filename:path>/<start:int>/<end:int>')
@app.route('/rrd/graph/<filename:path>', name='rrd-graph')
def rrd_graph(filename):
    # Response contents
    g = graph(filename)
    bottle.response.set_header('Content-Type', mimetype(g.args.get('imgformat')))
    return g.draw()

@app.route('/rrd/igraph/<filename>', name='rrd-igraph')
@bottle.view('rrd-igraph')
def rrd_graph_interactive(filename):
    return {
        'url': app.get_url('rrd-sgraph', filename=filename) 
               + '?%s' % bottle.request.query_string
    }

@app.route('/rrd/sgraph/<filename>', name='rrd-sgraph')
#@bottle.view('rrd-sgraph')
def rrd_graph_stream(filename):
    #FIXME: firefox wants to download the image(s)
    #       there's an awful lag before displaying the first image
    #FIXME: this is all quite buggy and tends to messup the server
    #       see with paste or gevent,
    #       http://bottlepy.org/docs/dev/recipes.html#keep-alive-requests
    import time
    step = float(bottle.request.query.get('step',
               rrd.info(os.path.join(config.rrd_basepath, filename)).get('step',
               5
    )))
    # Reponse headers
    boundary = '--boundarydonotcross'
    headers = {
        'Max-Age': 0,
        'Expires': 0,
        'Cache-Control': 'no-cache, private',
        'Pragma': 'no-cache',
        'Content-Type': 'multipart/x-mixed-replace; boundary=%s' % boundary,
        #'Transfer-Encoding': 'chunked'
    }
    for k, v in headers.items(): bottle.response.set_header(k, v)
    yield boundary
    yield "\r\n"
    while True:
        g = graph(filename)
        binary = g.draw()
        yield 'Content-Type: %s' % mimetype(g.args.get('imgformat'))
        yield "\r\n"
        yield 'Content-Length: %s' % len(binary)
        #yield "\r\n"
        #yield 'X-Timestamp: %s' % time.time()
        yield "\r\n\r\n"
        yield binary
        yield "\r\n"
        yield boundary
        yield "\r\n"
        time.sleep(step)

# View methods (fix route)
@app.route('/view', name='rrd-view')
def view_rrd_list():
    # Returns HTML of rrd list and urls
    rrds = [{'filename': filename,
             'info': app.get_url('rrd-info', filename=filename),
             'fetch': app.get_url('rrd-fetch', filename=filename),
             'graph': app.get_url('rrd-graph', filename=filename),
             'igraph': app.get_url('rrd-igraph', filename=filename)}
                 for filename in sorted(rrd_list().get('files')) or []]
    return bottle.template('views/rrd-list', rrds=rrds)

@app.route('/static/<file:path>', name='static')
def static(file):
    return bottle.static_file(file, root='')

@bottle.error(500)
def error(error):
    import json
    return json.dumps({'error': str(error.exception)})

def mimetype(imgformat=None):
    return {
        'PNG': 'image/png',
        'SVG': 'image/svg+xml',
        'EPS': 'application/postscript',
        'PDF': 'application/pdf'
    }.get(imgformat, 'image/png')

def graph(filename):
    "Returns a pyrrdtool.Graph object from the given filename,"
    "with data and style definitions"
    #FIXME: put the graph/data style application login into the 'style' module
    import style
    params = dict(bottle.request.params)
    # Applies option graph and data style definition
    if params.get('style'):
        stylefile = style.filename(params.get('style'), config.style_basepath)
        styledata = style.load(stylefile)
        del params['style']
        # Applies graph style
        params = dict(styledata.get('graph').items() + params.items())
        # Prepares data style (this pattern sucks, FIXME...)
        datastyle = styledata.get('data')

    # Creates pyrrdtool classes for graph rendering
    db = rrd.RRD.load(os.path.join(config.rrd_basepath, filename))
    data = [rrd.DEF.from_variable(rrd.Variable(db, ds.name))
            for ds in db.datasources]
    #FIXME: applies default style if no datastyle, datastyle otherwise
    #       this implementation sucks, refactor plz.
    try:
        datastyle
    except:
        style = [rrd.LINE.from_variable(variable, {'color':'555555'})
                 for variable in data]
    else:
        style = [getattr(rrd, datastyle.get(variable.vname).get('type')).from_variable(variable, datastyle.get(variable.vname))
                 for variable in data]

    return rrd.Graph(data, style, args=params)

def setup():
    "Setup logic"
    # Ensures rrd container path exists
    path = config.rrd_basepath
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path): pass
        else: raise

setup()
