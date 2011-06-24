from geometry import SE2
from . import graph_fix_node, random_connected_pose_network
from ..math import random_SE2
from . import assert_exact

def graph_fix_node_test():
    G = random_connected_pose_network(10)
    
    target = random_SE2()
    
    assert_exact(G)
    graph_fix_node(G, 0, target)
    SE2.assert_close(G.node[0]['pose'], target)
    assert_exact(G)
