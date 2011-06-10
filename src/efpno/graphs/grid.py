from ..math import SE2_from_translation_angle, pose_diff, np 
from . import DiGraph

import itertools

def grid_graph(nrows, ncols, side=5):
    ''' Creates a grid graph. '''
    G = DiGraph()
    coords2node = {}
    k = 0
    for i, j in itertools.product(range(nrows), range(ncols)):
        pose = SE2_from_translation_angle([i * side, j * side], 0)
        G.add_node(k, pose=pose)
        coords2node[(i, j)] = k 
        k += 1
        
    def connect(c1, c2):
        u = coords2node[c1]
        v = coords2node[c2]
        pose_u = G.node[u]['pose']
        pose_v = G.node[v]['pose']
        u_to_v = pose_diff(pose_u, pose_v)
        v_to_u = np.linalg.inv(u_to_v)
        G.add_edge(u, v, pose=u_to_v, weight=1.0)
        G.add_edge(v, u, pose=v_to_u, weight=1.0)
        
    for i, j in itertools.product(range(nrows), range(ncols)):
        if i > 0: connect((i, j), (i - 1, j)) # up
        if j > 0: connect((i, j), (i, j - 1)) # left
        
    return G
