import sys
import os
from efpno.parsing.graph_building import load_graph
from efpno.graphs.checking import assert_well_formed

EUCLIDEAN2D = 'E2D'

class TestCase(object):
    def __init__(self, tcid, G, geometry=EUCLIDEAN2D):
        self.tcid = tcid
        self.G = G
        self.has_ground_truth = False
    

    
import cPickle as pickle

def smart_load(filename, use_cache=True, progress=True, raise_if_unknown=True):
    ''' 
        If filename is 'stdin' it reads from stdin.
        
        If use_cache is True, it tries to read/write from a cache. 
        
        It returns a Graph object.
        
        G.graph['name'] is an id for the graph, derived from filename. 
    '''
    
    if filename == 'stdin':  
        if progress:
            sys.stderr.write('Reading from stdin.\n')
        G = load_graph(sys.stdin,
                       raise_if_unknown=raise_if_unknown,
                       progress=progress)
        G.graph['name'] = 'stdin'
        
    else:
        cache_name = os.path.splitext(filename)[0] + '.cache.pickle'
        if (use_cache and os.path.exists(cache_name) and
                    os.path.getmtime(cache_name) > os.path.getmtime(filename)):
            if progress:
                sys.stderr.write('Reading from cache %r.\n' % cache_name)
            with open(cache_name, 'rb') as f: 
                return pickle.load(f)
        
        if progress:
            sys.stderr.write('Reading from %r.\n' % filename)
        
        with open(filename) as f:
            G = load_graph(f,
                           raise_if_unknown=raise_if_unknown,
                           progress=progress)
            
        name = os.path.splitext(os.path.basename(filename))[0]        
        G.graph['name'] = name
        
        if use_cache:
            if progress:
                sys.stderr.write('Writing to cache %r.\n' % cache_name)
            with open(cache_name, 'wb') as f:
                pickle.dump(G, f)
    
    if G.number_of_nodes() == 0:
        raise Exception('Loaded graph with 0 nodes.')
    
    if G.number_of_edges() == 0:
        raise Exception('Loaded graph with 0 edges (%d nodes).' % 
                        G.number_of_nodes())

    assert_well_formed(G)    
    return G
    
# TODO: move away

def load_log_tc(filename):
    with open(filename) as f:
        G = load_graph(f)
    tc = TestCase(filename, G=G)
    return tc
