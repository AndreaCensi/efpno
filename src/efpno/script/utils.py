import networkx as nx
import time
from geometry import SE2
from geometry import translation_angle_from_SE2
from geometry.basic_utils import assert_allclose

from networkx.algorithms.shortest_paths.generic import *
from networkx.algorithms.shortest_paths.unweighted import *
import numpy as np 

def assert_inverse(pose1, pose2):
    d = SE2.multiply(pose1, pose2)
    assert_allclose(d, np.eye(3), atol=1e-8,
                     err_msg='Diff: %s' % SE2.friendly(d))
        
def check_proper(G):
    for u, v in G.edges():
        pose1 = G[u][v]['pose']
        pose2 = G[v][u]['pose']
        assert_inverse(pose1, pose2)
        
def timeit(func, *args, **kwargs):
    t0 = time.clock()
    res = func(*args, **kwargs)
    t1 = time.clock()
    cpu = t1 - t0
    print('%s(%s,%s): %s ms' % (func.__name__, args, kwargs, 1000 * cpu))
    return res

def SE2_to_distance(g):
    t = translation_angle_from_SE2(g)[0]
    return np.linalg.norm(t)


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

def area(a, b, c):
    M = np.ones((3, 3))
    M[0, :2] = a
    M[1, :2] = b
    M[2, :2] = c
    return np.linalg.det(M)


def direction(tail, head):
    v = head - tail
    return np.arctan2(v[1], v[0])

