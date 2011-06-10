from ..math import euclidean_distances, mds_randomized, np
from ..graphs import DiGraph
from . import poses2markers, markers2poses, markers_constraints


def improve_guess(G, G_guess):
    n = G.number_of_nodes()
    nodes = G.nodes()
    poses_guess = [ G_guess.node[u]['pose'] for u in nodes]
    print('Computing markers') 
    markers = poses2markers(poses_guess) # 2 x 3*n array
    print('Computing distances')
    D0 = euclidean_distances(markers)
    D = D0
    print('Markers constraints') 
    D_constraints = markers_constraints(G) 
    finite = np.isfinite(D_constraints)
    
    
    for k in range(3):
        print('K=%d ' % k)
        print('Setting constraints')
    
        D2 = np.where(finite, D_constraints, D)
        print('MDS')
        S = mds_randomized(D2, 2)
        print('Distances')
        D = euclidean_distances(S)
    
        change = np.abs(D - D0).mean()
        print('Mean change: %f' % change)
        
    poses = markers2poses(S)
    
    G2 = DiGraph()
    for i, u in enumerate(nodes):
        G2.add_node(u, pose=poses[i])
    return G2 

