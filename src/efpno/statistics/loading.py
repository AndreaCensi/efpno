from efpno.parsing.graph_building import load_graph 

EUCLIDEAN2D = 'E2D'

class TestCase(object):
    def __init__(self, tcid, G, geometry=EUCLIDEAN2D):
        self.tcid = tcid
        self.G = G
        self.has_ground_truth = False
    
# TODO: move away

def load_log_tc(filename):
    with open(filename) as f:
        G = load_graph(f)
    tc = TestCase(filename, G=G)
    return tc
