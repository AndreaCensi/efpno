import itertools
from contracts import contract
from ..math import np, SE2_to_distance, pose_average
from ..graphs import DiGraph , assert_well_formed

def randomly_permute(sequence):
    p = np.random.permutation(len(sequence))
    return [sequence[i] for i in p]
    
def weight_parallel(w1, w2):
    return w1 + w2

def weight_series(w1, w2):
    return 1.0 / (1.0 / w1 + 1.0 / w2)
    
@contract(returns='tuple(SE2, >0)')
def s_g_node_constraint(G, x, u, v):
    #assert G.has_edge(x, u), '%s not connected to %s' % (x, u)
    #assert G.has_edge(u, x), '%s not connected to %s' % (u, x)
    #assert G.has_edge(x, v), '%s not connected to %s' % (x, v)
    #assert G.has_edge(v, x), '%s not connected to %s' % (v, x)
    u_to_x = G[u][x]['pose']
    x_to_v = G[x][v]['pose']
    u_to_v = np.dot(u_to_x, x_to_v)
    w_u = G[u][x]['weight']
    w_v = G[v][x]['weight']
    weight = weight_series(w_u, w_v)
    return u_to_v, weight

def s_g_node_distance(G, n, u, v):
    constraint, weight = s_g_node_constraint(G, n, u, v) #@UnusedVariable
    return SE2_to_distance(constraint)

def s_g_possible_to_eliminate(G, x, max_distance):
    neighbors = G.neighbors(x)
    for u, v in itertools.product(neighbors, neighbors):
        if u == v: continue
        new_distance = s_g_node_distance(G, x, u, v)
        if new_distance > max_distance:
            # It would create an edge too big
            #print('Cannot eliminate %s -> %s -> %s, new dist = %f' % 
            #      (u, x, v, new_distance))
            return False
    return True

    
def simplify_graph(G0, max_dist):
    G = DiGraph(G0)
    
    assert_well_formed(G)
    
    for u, v in G.edges():
        G[u][v]['weight'] = 1.0
    
    nodes = randomly_permute(G.nodes())
    #print('Visiting in this order: %s' % nodes)
    
    for x in nodes:
        if not s_g_possible_to_eliminate(G, x, max_dist):
            #print('Cannot eliminate %s' % x)
            continue
        print('Eliminating %s' % x)
        neighbors = G.neighbors(x)
        for u, v in itertools.product(neighbors, neighbors):
            if u <= v: continue # make more elegant
            if u == v: continue
            #print('x=%s  u=%s v=%s' % (x, u, v))
            new_constraint, new_weight = s_g_node_constraint(G, x, u, v)
            
            if G.has_edge(u, v):
                old_constraint = G[u][v]['pose']
                old_weight = G[u][v]['weight']
                final_constraint = pose_average(
                                       poses=[old_constraint, new_constraint],
                                       weights=[old_weight, new_weight])
                final_weight = weight_parallel(old_weight, new_weight)
                # print('  %s --> %s is improved to weight %g' % (u, v, final_weight))
            else:
                final_constraint = new_constraint
                final_weight = new_weight
                G.add_edge(u, v)
                G.add_edge(v, u)
                # print('  %s --> %s is created at weight %g' % (u, v, final_weight))
            final_dist = SE2_to_distance(final_constraint)
            G.add_edge(u, v, dist=final_dist, weight=final_weight,
                             pose=final_constraint)
            G.add_edge(v, u, dist=final_dist, weight=final_weight,
                             pose=np.linalg.inv(final_constraint))

        # later, because the same edge can be used again        
        for u in neighbors:
            G.remove_edge(x, u)
            G.remove_edge(u, x)
        assert not G.neighbors(x)
        G.remove_node(x) 
    return G
