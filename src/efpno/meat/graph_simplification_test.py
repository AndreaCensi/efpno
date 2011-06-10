import contracts
from efpno.graphs import grid_graph, assert_exact
from efpno.meat import simplify_graph

def graph_simplification_test():
    contracts.disable_all()
    print('Generating random network')
#    G1 = random_connected_pose_network(n=100, max_t=100,
#                                       max_connection_dist=10,
#                                        connect_self=False)
    G1 = grid_graph(nrows=10, ncols=10, side=5)
    print('Checking random network')
    assert_exact(G1)
    # todo: remove some edges
    G2 = simplify_graph(G1, max_dist=20)
    
    assert_exact(G2)
    print 'before: ', G1.nodes()
    print 'after: ', G2.nodes()
