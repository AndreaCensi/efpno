from contracts import disable_all
from efpno.algorithms import EFPNO_S
from efpno.parsing import graph_write
from optparse import OptionParser
import sys
import numpy as np
from .loading import smart_load

usage = """

    %prog [options] [filename]  

    With no options, it reads from stdin.
    
    Other arguments:
        --slow  uses contracts checks
""" 

def main():
    parser = OptionParser(usage=usage)

    parser.add_option("--slow", default=False, action='store_true',
                      help='Enables sanity checks.')

    parser.add_option("--max_dist", default=15, type='float',
                      help='[= %default] Maximum distance for graph simplification.')
    parser.add_option("--min_nodes", default=250, type='float',
                      help='[= %default] Minimum number of nodes to simplify to.')
    parser.add_option("--scale", default=10000, type='float',
                      help='[= %default] Controls the weight of angular vs linear .')
    
    parser.add_option("--seed", default=42, type='int',
                      help='[= %default] Seed for random number generator.')
    
    (options, args) = parser.parse_args() #@UnusedVariable
    
    np.random.seed(options.seed)    
    
    if not options.slow:
        disable_all()
    # TODO: warn
    
    if len(args) > 1:
        raise Exception('Too many arguments')
    
    filename = args[0] if args else 'stdin'
    G = smart_load(filename, raise_if_unknown=True, progress=True)

    algorithm = EFPNO_S
    params = dict(max_dist=options.max_dist,
                  min_nodes=options.min_nodes,
                  scale=options.scale)
    
    instance = algorithm(params)
    results = instance.solve(G)

    G2 = results['solution']
    # G2 = results['G_landmarks']

    G2.graph['name'] = '%s-solved%dm' % (G.graph['name'], options.max_dist)
    graph_write(G2, sys.stdout)


if __name__ == '__main__':
    main()
