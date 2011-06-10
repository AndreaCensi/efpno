from ..parsing import AddVertex2D, AddEdge2D, parse 
from ..math import SE2_to_distance, SE2
from ..graphs import DiGraph

EUCLIDEAN2D = 'E2D'

class TestCase(object):
    def __init__(self, tcid, G, geometry=EUCLIDEAN2D):
        self.tcid = tcid
        self.G = G
        self.has_ground_truth = False
        self.geometry = geometry
#        
#    def is_spherical(self):
#        return self.geometry == 'S'
#    
#    def is_euclidean(self):
#        return self.geometry == 'E'
    
def load_graph(filename):
    G = DiGraph()
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
    return G

def load_log_tc(filename):
    tc = TestCase(filename, G=load_graph(filename))
    return tc
