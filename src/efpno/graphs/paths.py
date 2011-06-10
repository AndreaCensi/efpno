from ..math import SE2, np

def get_path(pred, i, j):
    nodes = [j]
    def last(): return nodes[0]
    
    while last() != i:
        nodes.append(pred[last()][i])
    
    path = []
    for i in range(len(nodes) - 1):
        path.append((nodes[i], nodes[i + 1]))    
    return path[::-1]
    
def check_good(G, i, j, path):
    if i == j:
        assert not path
        return
    
    assert path[0][0] == i
    assert path[-1][1] == i
    for e in path:
        assert G.has_edge(e)

    for k in range(len(path) - 1):
        assert path[k][1] == path[k + 1][0]
 
def reconstruct(G, path):
    pose = SE2.unity()
    for k in range(len(path) - 1):
        n1 = path[k]
        n2 = path[k + 1]
        edge = G[n1][n2]
        edge_pose = edge['pose']
        pose = np.dot(pose, edge_pose)
    return pose

    
