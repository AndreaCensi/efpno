from geometry import translation_angle_from_SE2
from optparse import OptionParser
import contracts
import numpy as np
import sys
from ..algorithms import EFPNO_S
from ..graphs import DiGraph
from ..parsing import (AddEdge2D, AddVertex2D, Equiv, SolveState, QueryState,
    graph_apply_operation, parse_command_stream)


def eprint(x):
    sys.stderr.write(x)
    sys.stderr.write('\n')
    sys.stderr.flush()
    
def main():
    usage = """Implements the interface of the SLAM evaluation utilities"""
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
    
    if not options.slow: contracts.disable_all()
    
    fin = sys.stdin
    fout = sys.stdout
    G = DiGraph()
    
    progress = False
    count = 0
    def status():
        return ('Read %5d commands, built graph with %5d nodes and %5d edges. \r' % 
                (count, G.number_of_nodes(), G.number_of_edges()))

    for command in parse_command_stream(fin, raise_if_unknown=False):
        if isinstance(command, (AddVertex2D, Equiv, AddEdge2D)):
            graph_apply_operation(G, command)
        elif isinstance(command, SolveState):
            eprint(status())
            algorithm = EFPNO_S
            params = dict(max_dist=options.max_dist,
                          min_nodes=options.min_nodes,
                          scale=options.scale)
            instance = algorithm(params)
            
            results = instance.solve(G)
            G = results['solution']
            
        elif isinstance(command, QueryState):
            nodes = command.ids if command.ids else G.nodes()
            nodes = sorted(nodes)
            
            fout.write('BEGIN\n')
            for n in nodes:
                t, theta = translation_angle_from_SE2(G.node[n]['pose'])
                fout.write('VERTEX_XYT %d %g %g %g\n' % 
                           (n, t[0], t[1], theta))
            fout.write('END\n')
            fout.flush()
        
        if progress and count % 250 == 0:
            eprint(status())
        count += 1

if __name__ == '__main__':
    main()
