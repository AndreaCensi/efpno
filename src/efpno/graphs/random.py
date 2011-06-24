import itertools
from ..math import random_SE2, SE2_to_distance, pose_diff
from . import DiGraph


def random_SE2_distribution(n, **kwargs):
    return [random_SE2(**kwargs) for i in range(n)] #@UnusedVariable

def random_connected_pose_network(n, max_t=10, max_connection_dist=None,
                                  connect_self=False):
    if max_connection_dist is None:
        max_connection_dist = max_t * 1000
        
    G = DiGraph()
    for i in range(n):
        G.add_node(i, pose=random_SE2(max_t=max_t))
    
    for i, j in itertools.product(range(n), range(n)):
        if i == j and not connect_self: continue
        pose_i = G.node[i]['pose']
        pose_j = G.node[j]['pose']
        i_to_j = pose_diff(pose_i, pose_j)
        dist = SE2_to_distance(i_to_j)
        G.add_edge(i, j, pose=i_to_j, dist=dist)
        
    return G

