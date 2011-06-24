import sys
from efpno.parsing.parse import parse_command_stream
from efpno.graphs import DiGraph
from efpno.parsing.structures import AddEdge2D, AddVertex2D, Equiv
from efpno.parsing.graph_building import graph_apply_operation
import contracts

def eprint(x):
    sys.stderr.write(x)
    sys.stderr.write('\n')
    sys.stderr.flush()
    
def main():
    usage = """Implements the interface of the SLAM evaluation utilities"""
    
    stream = sys.stdin
    
    contracts.disable_all()
    
    G = DiGraph()
    
    progress = True
    count = 0
    def status():
        return ('Reading graph: %5d commands  %5d nodes  %5d edges     \r' % 
                (count, G.number_of_nodes(), G.number_of_edges()))

    print('hello')
    for command in parse_command_stream(stream, raise_if_unknown=False):
        if isinstance(command, (AddVertex2D, Equiv, AddEdge2D)):
            glyph = {AddVertex2D:'.', Equiv:'=', AddEdge2D:'-'}
#            sys.stderr.write(glyph[command.__class__])
            graph_apply_operation(G, command)
        else:
            eprint('??? %s' % command.__repr__())
        
        if progress and count % 250 == 0:
            eprint(status())
        count += 1

if __name__ == '__main__':
    main()
