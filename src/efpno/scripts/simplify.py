import sys
from optparse import OptionParser
from contracts import disable_all
from ..parsing import graph_write, smart_load
from ..meat import simplify_graph_aggressive
from ..math import np

def main():
    np.seterr(all='raise')
    
    parser = OptionParser()

    parser.add_option("--plots", default=None)

    parser.add_option("--slow", default=False, action='store_true',
                      help='Enables sanity checks.')
    
    parser.add_option("--seed", default=None, type='int',
                      help='[= %default] Seed for random number generator.')
    
    parser.add_option("--min_nodes", default=250, type='int',
                      help='[= %default] Minimum number of nodes to simplify to.')

    parser.add_option("--max_dist", default=10, type='float',
                      help='[= %default] Maximum distance for graph simplification.')

    (options, args) = parser.parse_args() #@UnusedVariable
    
    np.random.seed(options.seed)    
    
    if not options.slow:
        disable_all()
    
    assert len(args) <= 1
    
    filename = args[0] if args else 'stdin'
    G = smart_load(filename, raise_if_unknown=True, progress=True)
        
    def eprint(x): sys.stderr.write('%s\n' % x)
     
    eprint('Loaded graph with %d nodes, %d edges.' % (G.number_of_nodes(),
                                                     G.number_of_edges()))

    G2, how_to_reattach = simplify_graph_aggressive(G, #@UnusedVariable
                                max_dist=options.max_dist,
                                min_nodes=options.min_nodes,
                                eprint=eprint)
    
    eprint('Reduced graph with %d nodes, %d edges.' % (G2.number_of_nodes(),
                                                     G2.number_of_edges()))
    G2.graph['name'] = '%s-sim%dm' % (G.graph['name'], options.max_dist)
    graph_write(G2, sys.stdout)
