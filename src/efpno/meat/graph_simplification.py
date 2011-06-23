import itertools
from contracts import contract
from ..math import np, SE2_to_distance, pose_average
from ..graphs import DiGraph , assert_well_formed
from efpno.graphs.performance import graph_degree_stats, \
    graph_degree_stats_compact
import sys

def randomly_permute(sequence):
    p = np.random.permutation(len(sequence))
    return [sequence[i] for i in p]
    
def weight_parallel(w1, w2):
    return w1 + w2

def weight_series(w1, w2):
    return 1.0 / (1.0 / w1 + 1.0 / w2)
#    
#def simplify_graph(G0, max_dist, eprint=None):
#    if eprint is None: eprint = lambda x: None #@UnusedVariable
#    how_to_reattach = []
#    G = DiGraph(G0)
#    
#    assert_well_formed(G)
#    
#    for u, v in G.edges():
#        G[u][v]['weight'] = 1.0
#    
#    nodes = np.array(randomly_permute(G.nodes()))
#    nodes_degree = np.array([len(G.neighbors(n)) for n in nodes])
#    max_degree = max(nodes_degree)
#    
#    nodes_order = [] 
#    for d in range(max_degree + 1):
#        nodes_with_degree = nodes[np.nonzero(nodes_degree == d)[0]]
#        eprint('degree %3d: %d nodes' % (d, len(nodes_with_degree)))
#        nodes_order.extend(nodes_with_degree.tolist())
#        
#    #print('Visiting in this order: %s' % nodes)
#    stats = []
#    def dstats(x, nneighbors):
#        global old_stats
#        new_stats = (G.number_of_nodes(), G.number_of_edges())
#        if stats:
#            old_stats = stats[-1]
#            eprint('%4d: %4d nei %4d nodes (%+3d) %4d (%+3d) edges' % 
#                  (x, nneighbors,
#                   new_stats[0], new_stats[0] - old_stats[0],
#                   new_stats[1], new_stats[1] - old_stats[1],))
#        stats.append(new_stats) 
#    
#    remaining = nodes_order
#    
#    for max_diff in [0, 0, 0, 0, 0, 0, 0,
#                     1, 0, 0, 0, 0, 0, 0,
#                     2, 0, 0, 0, 0, 0, 0,
#                     1, 0, 0, 0, 0, 0, 0,
#                     2, 0, 0, 0, 0, 0, 0,
#                     1, 0, 0, 0, 0, 0, 0,
#                     3, 0, 0, 0, 0]:
#        try_again = []
#        eprint('------------ %d,  remaining %d' % (max_diff, len(remaining)))
#        for x in remaining:
#            num_neighbors, before, after, dd = degree_diff(G, x) #@UnusedVariable
#    #        print('%s: diff %+3d' % (x, dd))
#            if dd > max_diff:
#                try_again.append(x)
#                continue
#            
#            reattach = possibly_eliminate(G, x, max_dist) 
#            if reattach:
#                dstats(x, num_neighbors)
#                how_to_reattach.append((x, reattach))
#            else:
#                try_again.append(x)
#                
#        remaining = try_again
#        
#    return G, how_to_reattach

def simplify_graph_aggressive(G0, max_dist, eprint=None):
    if eprint is None: eprint = lambda x: None #@UnusedVariable
    how_to_reattach = []
    G = DiGraph(G0)
    
    for n in G.nodes():
        G.node[n]['dirty'] = True
    
    assert_well_formed(G)
    
    for u, v in G.edges():
        G[u][v]['weight'] = 1.0
    
    nodes = np.array(randomly_permute(G.nodes()))
    nodes_degree = np.array([len(G.neighbors(n)) for n in nodes])
    max_degree = max(nodes_degree)
    
    nodes_order = [] 
    for d in range(max_degree + 1):
        nodes_with_degree = nodes[np.nonzero(nodes_degree == d)[0]]
        eprint('degree %3d: %d nodes' % (d, len(nodes_with_degree)))
        nodes_order.extend(nodes_with_degree.tolist())
         
    stats = []
    def dstats(x, nneighbors):
        global old_stats
        new_stats = (G.number_of_nodes(), G.number_of_edges())
        if stats:
            old_stats = stats[-1]
            if 0:
                eprint('%4d: %4d nei %4d nodes (%+3d) %4d (%+3d) edges' % 
                  (x, nneighbors,
                   new_stats[0], new_stats[0] - old_stats[0],
                   new_stats[1], new_stats[1] - old_stats[1],))
        stats.append(new_stats) 
    
    remaining = nodes_order
    # first remove everything with degree 2 (free lunch)
    eprint('Initial:\n%s' % graph_degree_stats_compact(G))
    
    remaining = remove_degree2(G, 2, remaining, how_to_reattach)
    eprint('Elim degree 2:\n%s' % graph_degree_stats_compact(G))
  
    current_max_diff = 0
    while True:
        try_again = []
        eprint('------------ max_diff %d,  remaining %6d nodes, %6d edges ' % 
                (current_max_diff, len(remaining), G.number_of_edges()))
        
        num_changes = 0
        num_cannot_be_changed = 0
        
        lowest_diff_remaining = 100000
        for x in remaining:
            num_neighbors, before, after, dd = degree_diff(G, x) #@UnusedVariable
            
            if current_max_diff > 1:
                if not s_g_possible_to_eliminate(G, x, max_dist):
                    num_cannot_be_changed += 1    
                    try_again.append(x)
                    continue
             
            if dd > current_max_diff:
                lowest_diff_remaining = min(lowest_diff_remaining, dd)
                try_again.append(x)
                continue
            
            reattach = possibly_eliminate(G, x, max_dist) 
            if reattach:
                dstats(x, num_neighbors)
                how_to_reattach.append((x, reattach))
                num_changes += 1
            else:
                num_cannot_be_changed += 1
                try_again.append(x)
                
        remaining = try_again
        eprint(' changed %5d, remaining %5d, %5d of which fixed    %s' % 
              (num_changes, len(remaining), num_cannot_be_changed,
               '' if num_changes else "wasted"))
        eprint('After:\n %s' % graph_degree_stats_compact(G))
        if num_changes:
            if num_changes > 50:
                current_max_diff = 0
                eprint(' too much changed, back to 0')
            else:
                eprint(' lowest diff is %d' % lowest_diff_remaining)
                current_max_diff = lowest_diff_remaining * 1
        else:
            if num_cannot_be_changed == len(try_again):
                break
            eprint(' lowest diff is %d' % lowest_diff_remaining)
            current_max_diff = lowest_diff_remaining * 1 
        
    return G, how_to_reattach

def remove_degree2(G, degree, remaining, how_to_reattach):
    try_again = []
    for x in remaining:
        num_neighbors, before, after, dd = degree_diff(G, x) #@UnusedVariable
        if num_neighbors != degree:
            try_again.append(x)
            continue
        
        reattach = possibly_eliminate(G, x, max_dist=100000) 
        if reattach:
            how_to_reattach.append((x, reattach))
    return try_again

def eliminate_links(G, x, u, v): 
    new_constraint, new_weight = s_g_node_constraint(G, x, u, v)
    
    if G.has_edge(u, v):
        old_constraint = G[u][v]['pose']
        old_weight = G[u][v]['weight']
        weights = np.array([old_weight, new_weight])
        weights = weights / np.sum(weights)
        final_constraint = pose_average(
                               poses=[old_constraint, new_constraint],
                               weights=weights)
        final_weight = weight_parallel(old_weight, new_weight) 
    else:
        final_constraint = new_constraint
        final_weight = new_weight
        G.add_edge(u, v)
        G.add_edge(v, u) 
    final_dist = SE2_to_distance(final_constraint)
    G.add_edge(u, v, dist=final_dist, weight=final_weight,
                     pose=final_constraint)
    G.add_edge(v, u, dist=final_dist, weight=final_weight,
                     pose=np.linalg.inv(final_constraint))
    
def possibly_eliminate(G, x, max_dist):
    ''' Returns either None, or an array {node -> x_to_node} for reattaching. '''
    if not s_g_possible_to_eliminate(G, x, max_dist):
        return False

    neighbors = G.neighbors(x)

    reduce = neighbors
#    if False and len(neighbors) > 6:
#        cliques = neighbors_cliques(G, x)
#        reduce = [list(m)[0] for m in cliques]
    
    if len(reduce) > 1:
        for u, v in itertools.product(reduce, reduce):
            if u <= v: continue # make more elegant
            eliminate_links(G, x, u, v)
        
    reattach = {}
    for u in neighbors:
        reattach[u] = (G[x][u]['pose'], G[x][u]['weight'])
        
    # later, because the same edge can be used again        
    for u in neighbors:
        G.remove_edge(x, u)
        G.remove_edge(u, x)
    assert not G.neighbors(x)
    G.remove_node(x) 
    assert not G.has_node(x)
    return reattach

def reattach(G0, how_to_reattach):
    G = DiGraph(G0)
    for x, constraints in reversed(how_to_reattach):
        neighbors = constraints.keys()
        #print('Reattaching %5d (%5d neigh: %s)' % (x, len(neighbors), neighbors))
        assert not G.has_node(x)
        for u in neighbors:
            assert G.has_node(u)
        poses = []
        weights = []
        for u in neighbors:
            x_to_u, weight = constraints[u]
            u_to_x = np.linalg.inv(x_to_u)
            pose_u = G.node[u]['pose']
            pose_x = np.dot(pose_u, u_to_x)
            poses.append(pose_x)
            weights.append(weight)
        weights = np.array(weights)
        weights = weights / np.sum(weights)
        best = pose_average(poses, weights)
        G.add_node(x, pose=best)
    return G
 
  
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

def neighbors_cliques(G, x):
    neighbors = G.neighbors(x)
    neighbors2clique = {}
    clique2nodes = {}
    for n in neighbors:
        clique2nodes[n] = set([n]) 
        neighbors2clique[n] = n
    
    def join_cliques(c1, c2):
        if c1 == c2: return
        for n in clique2nodes[c2]:
            neighbors2clique[n] = c1
        clique2nodes[c1].update(clique2nodes[c2])
        del clique2nodes[c2]
            
    for u, v in itertools.product(neighbors, neighbors):
        if G.has_edge(u, v):
            join_cliques(neighbors2clique[u], neighbors2clique[v]) 

    return [list(x) for x in clique2nodes.values()]


def degree_diff(G, x):
    neighbors = G.neighbors(x)
    n = len(neighbors)
    before = n
    for u, v in itertools.product(neighbors, neighbors):
        if u <= v: continue
        if G.has_edge(u, v):
            before += 1
    after = n * (n - 1) / 2
    dd = after - before
    
    return n, before, after, dd
