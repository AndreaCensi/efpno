from ..math import assert_allclose
from ..graphs import random_connected_pose_network, graph_errors, graph_errors_print
from . import solve_by_reduction
#
#def remove_edges_longer_that(G, max_dist):
#    for x in G.nodes():
#        for y in G.neighbors(x):
#            if G[x][y]['dist'] > max_dist

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
