import sys, numpy as np
from efpno.script.loading import  smart_load
from efpno.parsing.write import graph_write
from optparse import OptionParser 
from contracts.enabling import disable_all 
from efpno.algorithms.simplification import EFPNO_S

usage = """

    %cmd   [--outdir DIRECTORY]   [filename]  

    Other arguments:
        --fast  does not use contracts checks
""" 

def main():
    parser = OptionParser(usage=usage)

    parser.add_option("--outdir", default='.')
    
    parser.add_option("--fast", default=False, action='store_true',
                      help='Disables sanity checks.')

    parser.add_option("--max_dist", default=10, type='float',
                      help='[= %default] Maximum distance for graph simplification.')

    parser.add_option("--seed", default=None, type='int',
                      help='[= %default] Seed for random number generator.')
    
    (options, args) = parser.parse_args() #@UnusedVariable
    
    np.random.seed(options.seed)    
    
    if options.fast:
        disable_all()
    
    if len(args) > 1:
        raise Exception('Too many arguments')
    
    filename = args[0] if args else 'stdin'
    G = smart_load(filename, raise_if_unknown=True, progress=True)

    algorithm = EFPNO_S
    params = dict(max_dist=options.max_dist)
    
    instance = algorithm(params)
    results = instance.solve(G)

    G2 = results['solution']
#    G2 = results['G_landmarks']

    G2.graph['name'] = '%s-solved%dm' % (G.graph['name'], options.max_dist)
    graph_write(G2, sys.stdout)


if __name__ == '__main__':
    main()
