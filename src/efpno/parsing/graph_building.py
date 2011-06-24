import sys

from ..math import SE2_to_distance, SE2
from ..graphs import DiGraph

from . import AddVertex2D, AddEdge2D, parse, Equiv 

def merge_nodes(G, x, y):
    """ Merges x with y (removes y, keeps x). """
    if not G.has_node(x):
        raise Exception('No node %s present (merge %s and %s)' % (x, x, y))
    if not G.has_node(y):
        raise Exception('No node %s present (merge %s and %s)' % (y, x, y))
    
    if G.has_edge(x, y): 
        G.remove_edge(x, y)
        G.remove_edge(y, x)
        
    for u in G.neighbors(y):
        if u == x: 
            continue
        G.add_edge(x, u)
        G.add_edge(u, x)
        attrs = ['pose', 'dist', 'inf']
        for att in attrs:
            G[x][u][att] = G[y][u][att]
            G[u][x][att] = G[u][y][att]
    
    
    G.remove_node(y)
    
def load_graph(stream, raise_if_unknown=True, progress=True):
    G = DiGraph()
    
    # old_id -> new_id
    merged = {}
    def node_name(s):
        # use integers for node names
        name = int(s)
        # resolve name from merged database
        while name in merged:
            name = merged[name]
        return name
    
    count = 0
    def status():
        return ('Reading graph: %5d commands  %5d nodes  %5d edges     \r' % 
                (count, G.number_of_nodes(), G.number_of_edges()))
        
    for x in parse(stream, raise_if_unknown=raise_if_unknown):
        if isinstance(x, AddVertex2D):
            node = node_name(x.id)
            if G.has_node(node):
                raise Exception('Cannot add again node %r' % node)
            G.add_node(node, pose=x.pose) 
    
        if isinstance(x, Equiv):
            node1 = node_name(x.id1)
            node2 = node_name(x.id2)
            merge_nodes(G, node1, node2)
            # keep track of synonyms 
            merged[node2] = node1
            
        if isinstance(x, AddEdge2D):
            node1 = node_name(x.id1)
            node2 = node_name(x.id2)
            
            if node1 == node2:
                #sys.stderr.write('Not adding edge between %s (%s) and %s (%s)\n' % 
                #                 (x.id1, node1, x.id2, node2))
                continue
            
            G.add_edge(node1, node2, pose=x.pose, inf=x.inf,
                        dist=SE2_to_distance(x.pose))
            G.add_edge(node2, node1, pose=SE2.inverse(x.pose), inf=x.inf,
                       dist=SE2_to_distance(x.pose))
    
        if progress and (count % 100 == 0):
            sys.stderr.write(status())
            sys.stderr.flush()
        count += 1
    if progress and (count % 100 == 0):
        sys.stderr.write(status())
        sys.stderr.write('\n')
        sys.stderr.flush()
    return G

def eprint(x):
    sys.stderr.write(x)
    sys.stderr.write('\n')
    
def graph_apply_operation(G, op):
    if not 'merged' in G.graph:
        G.graph['merged'] = {} 
    
    # old_id -> new_id
    merged = G.graph['merged']
    
    def node_name(s):
        # use integers for node names
        name = int(s)
        # resolve name from merged database
        while name in merged:
            name = merged[name]
        return name
    
    if isinstance(op, AddVertex2D):
        node = node_name(op.id)
        if G.has_node(node):
            pass
            eprint('Warning: adding again node %r (pose: %s)' % (op.id, op.pose))
        else:
            assert isinstance(node, int)
            G.add_node(node, pose=op.pose) 

    elif isinstance(op, Equiv):
        node1 = node_name(op.id1)
        node2 = node_name(op.id2)
        merge_nodes(G, node1, node2)
        # keep track of synonyms 
        merged[node2] = node1
        
    elif isinstance(op, AddEdge2D):
        node1 = node_name(op.id1)
        node2 = node_name(op.id2)
        
        if node1 == node2:
            #eprint('Not adding edge between %s (%s) and %s (%s)\n' % 
            #                 (op.id1, node1, op.id2, node2))
            return

        if G.has_edge(node1, node2):
            #eprint('Warning: already have edge between %s (%s) and %s (%s)\n' % 
            #                 (op.id1, node1, op.id2, node2))
            pass
        
        assert isinstance(node1, int)
        assert isinstance(node2, int)
        G.add_edge(node1, node2, pose=op.pose, inf=op.inf,
                    dist=SE2_to_distance(op.pose))
        G.add_edge(node2, node1, pose=SE2.inverse(op.pose), inf=op.inf,
                   dist=SE2_to_distance(op.pose))
    else:
        raise Exception('Unknown operation %r' % op)


