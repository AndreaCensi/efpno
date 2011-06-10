import sys
from optparse import OptionParser
from contracts import disable_all
from ..math import np
from ..meat import simplify_graph
from .loading import load_graph

def main():
    parser = OptionParser()

    parser.add_option("--plots", default=None)

    parser.add_option("--fast", default=False, action='store_true',
                      help='Disables sanity checks.')
    
    parser.add_option("--seed", default=None, type='int',
                      help='[= %default] Seed for random number generator.')
    
    parser.add_option("--max_dist", default=1, type='float',
                      help='[= %default] Seed for random number generator.')

    (options, args) = parser.parse_args() #@UnusedVariable
    
    np.random.seed(options.seed)    
    
    if options.fast:
        disable_all()
    
    assert len(args) <= 1
    if args:
        f = open(args[0])
    else:
        f = sys.stdin
    G = load_graph(f, raise_if_unknown=True, progress=True)

    print('Loaded graph with %d nodes, %d edges.' % (G.number_of_nodes(),
                                                     G.number_of_edges()))

    G2 = simplify_graph(G, max_dist=options.max_dist)
    
    print('Reduced graph with %d nodes, %d edges.' % (G2.number_of_nodes(),
                                                     G2.number_of_edges()))
