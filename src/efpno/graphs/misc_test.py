from geometry import SE2
from . import graph_fix_node, random_connected_pose_network
from ..math import random_SE2

def graph_fix_node_test():
    G = random_connected_pose_network(10)
    
    target = random_SE2()
    
    graph_fix_node(G, 0, target)
    SE2.assert_close(G.node[0]['pose'], target)
