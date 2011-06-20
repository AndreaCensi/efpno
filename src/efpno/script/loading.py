from ..parsing import AddVertex2D, AddEdge2D, parse 
from ..math import SE2_to_distance, SE2
from ..graphs import DiGraph
import sys

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
    
def load_graph(stream, raise_if_unknown=True, progress=True):
    G = DiGraph()
    count = 0
    for x in parse(stream, raise_if_unknown=raise_if_unknown):
        if isinstance(x, AddVertex2D):
            G.add_node(int(x.id), pose=x.pose)
            
        if isinstance(x, AddEdge2D):
            G.add_edge(int(x.id1), int(x.id2), pose=x.pose, inf=x.inf,
                        dist=SE2_to_distance(x.pose))
            G.add_edge(int(x.id2), int(x.id1), pose=SE2.inverse(x.pose), inf=x.inf,
                       dist=SE2_to_distance(x.pose))
    
        if progress and (count % 100 == 0):
            sys.stderr.write('Reading graph: %5d    \r' % count)
            sys.stderr.flush()
        count += 1
    return G

def load_log_tc(filename):
    with open(filename) as f:
        G = load_graph(f)
    tc = TestCase(filename, G=G)
    return tc
