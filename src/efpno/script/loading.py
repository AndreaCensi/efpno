import networkx as nx
from efpno.parsing.parse import parse
from efpno.parsing.structures import AddVertex2D, AddEdge2D 
from .utils import SE2_to_distance, check_proper
from geometry.manifolds import SE2

def load_graph(filename):
    G = nx.DiGraph()
    raise_if_unknown = True
    count = 0
    with open(filename) as f:
        for x in parse(f, raise_if_unknown=raise_if_unknown):
            if isinstance(x, AddVertex2D):
                G.add_node(int(x.id))
                
            if isinstance(x, AddEdge2D):
                G.add_edge(int(x.id1), int(x.id2), pose=x.pose, inf=x.inf,
                            dist=SE2_to_distance(x.pose))
                G.add_edge(int(x.id2), int(x.id1), pose=SE2.inverse(x.pose), inf=x.inf,
                           dist=SE2_to_distance(x.pose))
        
            if count % 100 == 0:
                print count
            count += 1
    check_proper(G)
    return G
