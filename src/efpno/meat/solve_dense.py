import itertools
from ..math import (
                    np, mds, SE2_from_translation_angle,
                    SE2, area, SE2_to_distance, assert_allclose,
                    euclidean_distances
                    )
from ..graphs import (
                      DiGraph, all_pairs_shortest_path, reconstruct,
                       assert_same_nodes
                      )
from . import poses2markers, markers2poses

def extract_distances(G):
    # TODO: check dense
    n = G.number_of_nodes()
    D = np.zeros((n, n))
    it2node = G.nodes()
#    node2it = dict([(node, it) for it, node in enumerate(it2node) ])
    for i, j in itertools.product(range(n), range(n)):
        if i == j: continue
        u = it2node[i]
        v = it2node[j]
        D[i, j] = G[u][v]['dist']
        assert D[i, j] > 0
    return D

def solve_euclidean(G):
    D = extract_distances(G) 
    S = mds(D, 2)

    G2 = DiGraph()
    n = G.number_of_nodes()
    for i in range(n):    
#        u = G.neighbours(i)[0]
#        constraint = G[i][u]['pose']
        theta = 0
        node_pose = SE2_from_translation_angle(S[:, i], theta) 
        G2.add_node(i, pose=node_pose)
    return G2, S, D

def markers_constraints(G, scale=1):
    n = G.number_of_nodes()
    Dall = np.ones((3 * n, 3 * n)) * np.inf
    it2node = G.nodes()
    node2it = dict([(node, it) for it, node in enumerate(it2node) ])
    for u, v in G.edges():
        i = node2it[u]
        j = node2it[v]        
        pose = G[u][v]['pose']
        markers = poses2markers([ SE2.unity(), pose], scale=scale)
        Dset = euclidean_distances(markers)
        indices = [i, j, i + n, j + n, i + 2 * n, j + 2 * n]
        for r, s in itertools.product(range(6), range(6)):
            Dall[indices[r], indices[s]] = Dset[r, s]
    return Dall

def markers_constraints_sparse(G, scale=1):
    n = G.number_of_nodes()
#    Dall = np.ones((3 * n, 3 * n)) * np.inf
    it2node = G.nodes()
    node2it = dict([(node, it) for it, node in enumerate(it2node) ])
    
    Dall = {}
    for i in range(3 * n):
        Dall[i] = {}
    for u, v in G.edges():
        i = node2it[u]
        j = node2it[v]        
        pose = G[u][v]['pose']
        markers = poses2markers([ SE2.unity(), pose], scale=scale)
        Dset = euclidean_distances(markers)
        indices = [i, j, i + n, j + n, i + 2 * n, j + 2 * n]
        for r, s in itertools.product(range(6), range(6)):
            Dall[indices[r]][indices[s]] = Dset[r, s]
    return Dall

def solve_by_reduction(G, scale=1):
    ''' G: fully connected. '''
    n = G.number_of_nodes()
    print('solve_by_reduction: Markers constraints')
    Dall = markers_constraints(G, scale=scale)
    print('solve_by_reduction: MDS')
    Sall = mds(Dall, 2)
    # Check that we have the correct orientation
    areas = np.array([area(Sall[:, i], Sall[:, i + n], Sall[:, i + 2 * n]) 
                        for i in range(n)])
    if np.mean(np.sign(areas)) < 0:
        # Invert one coordintate to flip orientation
        Sall[0, :] = -Sall[0, :]
    
    G2 = DiGraph() 
    print('solve_by_reduction: marker to pose')
    poses = markers2poses(Sall)
    it2node = G.nodes()
    for i, pose in enumerate(poses):
        G2.add_node(it2node[i], pose=pose)
    return G2


def compute_fully_connected_subgraph(G,
            paths, landmarks=None, node_ids=None, add_self=False):
    ''' Creates the fully-connect graph from G.
        If landmarks is None, it defaults to all nodes. ''' 
    S = DiGraph()
    if landmarks is None:
        landmarks = G.nodes()
        node_ids = landmarks
    nlandmarks = len(landmarks)
    if node_ids is None:
        node_ids = range(nlandmarks)
    for i in range(nlandmarks):
        for j in range(nlandmarks):
            if i == j and not add_self: continue
            u, v = landmarks[i], landmarks[j]
            pose = reconstruct(G, paths[u][v])
            dist = SE2_to_distance(pose)
            S.add_edge(node_ids[i], node_ids[j], pose=pose, dist=dist)
            
    if add_self:
        for i in range(nlandmarks):
            dist = S[i][i]['dist']
            assert_allclose(dist, 0)
#            v_to_u = reconstruct(G, paths[u][v][::-1]) 
#            assert_inverse(u_to_v, v_to_u)
    return S
    
 
def solve_dense(G, fix_node=None, fix_pose=SE2.unity()):
    paths = all_pairs_shortest_path(G)
    Gfull = compute_subgraph(G, paths, landmarks=G.nodes(), node_ids=G.nodes())
    assert_same_nodes(G, Gfull)
    G2 = solve_by_reduction(Gfull)
    assert_same_nodes(G2, Gfull)
    if fix_node is not None:
        pose = G2.node[fix_node]['pose'] 
        diff = np.dot(fix_pose, np.linalg.inv(pose))
        for u in G2.nodes():
            G2.node[u]['pose'] = np.dot(diff, G2.node[u]['pose']) 
      
    return G2  
    
