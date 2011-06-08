from efpno.script.efpno2 import solve_by_reduction
from efpno.script.performance import graph_errors, graph_errors_print
from geometry.poses import SE2_from_translation_angle
import numpy as np
import networkx as nx #@UnresolvedImport
import itertools
from geometry.basic_utils import assert_allclose
from .utils import SE2_to_distance

def random_SE2():
    t = np.random.randn(2) * 10
    theta = np.random.rand() * np.pi * 2
    return SE2_from_translation_angle(t, theta)

def random_SE2_distribution(n):
    return [random_SE2() for i in range(n)] #@UnusedVariable


def random_connected_pose_network(n, connect_self=False):
    G = nx.DiGraph()
    for i in range(n):
        G.add_node(i, pose=random_SE2())
    
    for i, j in itertools.product(range(n), range(n)):
        if i == j and not connect_self: continue
        pose_i = G.node[i]['pose']
        pose_j = G.node[j]['pose']
        i_to_j = np.dot(np.linalg.inv(pose_i), pose_j)
        dist = SE2_to_distance(i_to_j)
        G.add_edge(i, j, pose=i_to_j, dist=dist)
        
    return G

def solve_by_reduction_test():
    for i in range(5):
        G1 = random_connected_pose_network(n=10)
        G2 = solve_by_reduction(G1)
        stats11 = graph_errors(G1, G1)
        print(graph_errors_print('stats11', stats11))
        assert_allclose(stats11['errors_t_max'], 0, atol=1e-8)
        assert_allclose(stats11['errors_theta_max'], 0, atol=1e-8)
    #    stats22 = graph_errors(G2, G2)
    #    print(graph_errors_print('stats22', stats22))
        stats12 = graph_errors(G1, G2)
        print(graph_errors_print('stats12', stats12))
        assert_allclose(stats12['errors_t_max'], 0, atol=1e-8)
        assert_allclose(stats12['errors_theta_max'], 0, atol=1e-8)
#    stats21 = graph_errors(G2, G1)
#    print(graph_errors_print('stats21', stats21))
