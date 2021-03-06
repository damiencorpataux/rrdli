"A pyrrdtool style module"
#FIXME: manage the concept of a color palette
#       for enabling to name colors,
#       and automatic coloring of DataStyle: a nice palette
#       can be a nice default for DataStyle colors.

import os, json

def load(filename):
    """parses filename json content into a python dict,
    recursively merging 'inherit'ed files content"""
    def walk(style):
        keys = style.keys()
        for k in keys:
            if isinstance(style[k], dict): walk(style[k])
            elif k == 'inherit':
                f = globals()['filename'](style[k], os.path.dirname(filename))
                style = merge(style, load(f))
                del style[k]
        return style 
    
    try:
        with open(filename) as file: style = walk(json.load(file))
    except Exception as e:
        raise Exception("Loading style '%s' failed: %s" % (filename, e))
    return style

def filename(stylename, basepath=''):
    """returns a filename from the given stylename, eg.
    some/style            -> some/style.json
    some/style, base/path -> base/path/some/style.json"""
    return os.path.join(basepath, stylename + os.path.extsep + 'json')


def merge(a, b):
    """recursively merges dict's. not just simple a['key'] = b['key'], if
    both a and bhave a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary."""
    'Taken from http://www.xormedia.com/recursively-merge-dictionaries-in-python/'
    #FIXME: deepcopy might not be needed
    from copy import deepcopy
    if not isinstance(b, dict):
        return b
    result = deepcopy(a)
    for k, v in b.iteritems():
        if k in result and isinstance(result[k], dict):
                result[k] = merge(result[k], v)
        else:
            result[k] = deepcopy(v)
    return result

if __name__ == '__main__':
    import pprint as pp
    r = load('styles/ping.json')
    pp.pprint(r)
