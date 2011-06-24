import itertools
from contracts import contract
from ..math import np, SE2_to_distance, pose_average
from ..graphs import DiGraph , assert_well_formed, graph_degree_stats_compact


def randomly_permute(sequence):
    p = np.random.permutation(len(sequence))
    return [sequence[i] for i in p]
    
def weight_parallel(w1, w2):
    return w1 + w2

def weight_series(w1, w2):
    return 1.0 / (1.0 / w1 + 1.0 / w2)


def simplify_graph_aggressive(G0, max_dist, eprint=None, min_nodes=0):
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
        nodes_order.extend(nodes_with_degree.tolist())
         
    remaining = nodes_order
    
    eprint('First remove the nodes with degree 2') # TODO:
    # first remove every node with degree 2 
    remaining = s_g_remove_degree2(G, 2, remaining, how_to_reattach)
    eprint('Remaining with %d nodes. Now iterating on the others.' % 
           len(remaining))
    
    current_max_diff = 0
    num_iteration = 0
    while len(remaining) > min_nodes:
        # Some debug information
        num_iteration += 1
        num_nodes_before = G.number_of_nodes()
        num_edges_before = G.number_of_edges()
        
        # Nodes that could not be removed
        try_again = []
         
        num_changes = 0
        num_cannot_be_changed = 0
        
        lowest_diff_remaining = 100000
        for x in remaining:
            num_neighbors, before, after, dd = degree_diff(G, x) #@UnusedVariable
            
            if dd > current_max_diff:
                lowest_diff_remaining = min(lowest_diff_remaining, dd)
                try_again.append(x)
                continue
            
            if s_g_possible_to_eliminate(G, x, max_dist):
                reattach = s_g_eliminate_node(G, x) 
                how_to_reattach.append((x, reattach))
                num_changes += 1
            else:
                num_cannot_be_changed += 1
                try_again.append(x)
                
            if len(remaining) - num_changes <= min_nodes: break
                
        remaining = try_again
    
        if num_changes:
            if num_changes > 50:
                current_max_diff = 0
            else:
                current_max_diff = lowest_diff_remaining
        else:
            if num_cannot_be_changed == len(try_again):
                break
            current_max_diff = lowest_diff_remaining 
        
        if current_max_diff > 0:
            current_max_diff *= 2
            
        eprint('it %3d: before: %5d nodes, %5d edges; max_diff: %2d,'
               ' changed %5d, now %5d nodes (fixed: %5d), min_diff: %5d' % 
              (num_iteration,
               num_nodes_before,
               num_edges_before,
               current_max_diff,
               num_changes,
               len(remaining),
               num_cannot_be_changed,
               lowest_diff_remaining))

    return G, how_to_reattach

def s_g_remove_degree2(G, degree, remaining, how_to_reattach):
    try_again = []
    for x in remaining:
        num_neighbors, before, after, dd = degree_diff(G, x) #@UnusedVariable
        if num_neighbors != degree:
            try_again.append(x)
            continue
        
        reattach = s_g_eliminate_node(G, x)
        how_to_reattach.append((x, reattach))
    return try_again

def s_g_eliminate_links(G, x, u, v): 
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
    
def s_g_eliminate_node(G, x):
    ''' Returns an array {node -> x_to_node} for reattaching. '''

    neighbors = G.neighbors(x)

    reduce = neighbors
    max_neighbors = 9
    if True and len(neighbors) > max_neighbors:
        cliques = neighbors_cliques(G, x)
        reduce = [list(m)[0] for m in cliques]
        
        remaining = list(neighbors)
        for r in reduce: remaining.remove(r)
        while len(reduce) < max_neighbors:
            reduce.append(remaining.pop(np.random.randint(len(remaining) - 1)))
    
    if len(reduce) > 1:
        for u, v in itertools.product(reduce, reduce):
            if u <= v: continue # make more elegant
            s_g_eliminate_links(G, x, u, v)
        
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
 
  
def s_g_node_constraint(G, x, u, v):
    ''' returns a tuple (pose, weight) '''
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
