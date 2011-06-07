import networkx as nx
from efpno.parsing.parse import parse
import sys
from efpno.parsing.structures import AddVertex2D, AddEdge2D
import time
import compmake
from reprep import Report
from geometry import mds, place
from geometry import SE2
from geometry.poses import translation_angle_from_SE2
from contracts.main import contract
#
#def disk_cache(func):
#    import os, cPickle as pickle
#    # Processes a file or directory, caching results 
#    # Assumes that the wrapped function has only one arg (for simplicity).
#    def wrapper(filename):
#        if os.path.isdir(filename):
#            cache = os.path.join(filename, '%s.pickle' % func.__name__)
#        else:
#            cache = os.path.splitext(filename)[0] + '.%s.pickle' % func.__name__
#        if (os.path.exists(cache) and
#            (os.path.getmtime(cache) > os.path.getmtime(filename))):
#            # print('Using cache %r' % cache)
#            return pickle.load(open(cache, 'rb'))
#        else:
#            # print('Creating cache %r' % cache)
#            result = func(filename)
#            with open(cache, 'wb') as f:
#                pickle.dump(result, f)
#            return result
#    return wrapper

#@disk_cache
def load_graph(filename):
    G = nx.Graph()
    raise_if_unknown = True
    count = 0
    with open(filename) as f:
        for x in parse(f, raise_if_unknown=raise_if_unknown):
            if isinstance(x, AddVertex2D):
                G.add_node(int(x.id))
                
            if isinstance(x, AddEdge2D):
                G.add_edge(int(x.id1), int(x.id2), pose=x, inf=x.inf)
            
            if count % 100 == 0:
                print count
            count += 1
    return G

from networkx.algorithms.shortest_paths.dense import *


def my_distances(G):
    graphs = {}
    graphs[0] = G
    adjs = {}
    adjs[0] = nx.to_numpy_matrix(G)
     
    for k in range(5):
        print('k =  %s' % k)
        sub = graphs[k]
        current = nx.Graph()
        for u in G.nodes():
            current.add_node(u)
         
        for u in sub:
            for v in sub.neighbors(u):
                for w in sub.neighbors(v):
                    if w not in sub.neighbors(u): 
                        current.add_edge(u, w)

        graphs[k + 1] = current
        adjs[k + 1] = nx.to_numpy_matrix(current)

    return G2
    
def my_floyd_warshall_numpy(G, nodelist=None, weight='weight'):
#    G = closure(G0)
#    G = G0
    
    try:
        import numpy as np
    except ImportError:
        raise ImportError(\
          "to_numpy_matrix() requires numpy: http://scipy.org/ ")
    A = nx.to_numpy_matrix(G, nodelist=nodelist, multigraph_weight=min,
                         weight=weight)
    
    
    n, m = A.shape
    I = np.identity(n)
#    A[A == 0] = np.inf # set zero entries to inf
    A[A == 0] = 1000 # set zero entries to inf
    A[I == 1] = 0 # except diagonal which should be zero
    A = A.astype('int32')
    
    rp = np.random.permutation(n)
    
#    for k in range(n):
    cn = int(n / 10)
    ci = np.random.permutation(n)[:cn]
    print('Core %d/%d' % (cn, n))
    Ac = A[ci, :][:, ci]
    for j in np.random.permutation(cn):
        r = Ac[j, :]
        Ac = np.minimum(Ac, r + r.T)
#
    for j in range(n):
        A[ci[j], ci] = Ac[j, :]
           
    print('Core done')
    
    for k in np.random.permutation(n):
        i = k % n
        r = A[i, :]
        A2 = np.minimum(A, r + r.T)
#        change = (A - A2)
        changes = (A - A2)
        change_max = changes.max()
        change_mean = changes.mean()
#        finite = np.isfinite(change)
#        change = change[finite].max()
        print('it %6d %6d: change max %8d  mean %8.5f' % (k, i, change_max, change_mean))
        A = A2
    return A

def timeit(func, *args, **kwargs):
    t0 = time.clock()
    res = func(*args, **kwargs)
    t1 = time.clock()
    cpu = t1 - t0
    
    print('%s(%s,%s): %s ms' % (func.__name__, args, kwargs, 1000 * cpu))
    return res

def SE2_to_distance(g):
    pass 

from compmake import comp, compmake_console
import numpy as np

def f_w(G):
    p, d = floyd_warshall_predecessor_and_distance(G)
    n = G.number_of_nodes()
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            D[i, j] = d[i][j]
    return p, D

def write_report(tc, results, filename):
    D = tc['p_d'][1]
    pred = tc['p_d'][0]
    r = Report()
    f = r.figure('misc')
    r.data('D', D).display('scale').add_to(f)
    
    for i in range(D.shape[0]):
        D[i, i] = 0
#    s = mds(D, 2)
    
    Dl = results['Dl']
    Sl = results['Sl']
    S = results['S']
    
    
    report_add_coordinates(r, 'Sl', Sl, f, 'landmarks positions') 
    report_add_coordinates(r, 'S', S, f, 'all positions') 
        
    r.data('Dl', Dl).display('scale').add_to(f)
    
    print('Writing to %r.' % filename)
    r.to_html(filename)

@contract(S='array[2xN]')
def report_add_coordinates(r, nid, S, f=None, caption=None):
    print S
    with  r.data_pylab(nid) as pylab:
        pylab.plot(S[0, :], S[1, :], 'r.')
        pylab.axis('equal')
    if f:
        r.last().add_to(f, caption)
    

print('ciao2')

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
 
from networkx.algorithms.shortest_paths.generic import *
from networkx.algorithms.shortest_paths.unweighted import *

def reconstruct(G, path):
    pose = SE2.unity()
    for k in range(len(path) - 1):
        n1 = path[k]
        n2 = path[k + 1]
        edge = G[n1][n2]
        edge_pose = edge['pose'].pose # FIXME: change this
        pose = np.dot(pose, edge_pose)
    return pose


def efpno2(tc):
    G = tc['G']
    D = tc['p_d'][1]
    pred = tc['p_d'][0]
    n = D.shape[0]
    
    for i in range(n):
        D[i, i] = 0
    results = {}    
    paths = timeit(all_pairs_shortest_path, G)
    
    D = np.zeros((n, n))
    
    freq = 10
    landmarks = range(0, n, freq)
    print('Using landmarks: %s' % landmarks)
    nlandmarks = len(landmarks)
    landmarks_constraints = {}
    Dl = np.zeros((nlandmarks, nlandmarks))
    for i in range(nlandmarks):
        landmarks_constraints[i] = {}
        print('i=%d/%d' % (i, nlandmarks))
        for j in range(nlandmarks):
            u = landmarks[i]
            v = landmarks[j]
            diff = reconstruct(G, paths[u][v])
            t, theta = translation_angle_from_SE2(diff)
            Dl[i, j] = np.linalg.norm(t)
            landmarks_constraints[i][j] = diff
    Sl = mds(Dl, 2)
    
    S = np.zeros((2, n))
    for i in range(n):
        i_to_landmarks = [(l, len(paths[i][landmarks[l]])) 
                          for l in range(nlandmarks)]
        nref = 3
        shortest = sorted(i_to_landmarks, key=lambda x:x[1])[:nref]
        references = np.zeros((2, nref))
        distances = np.zeros(nref)
        for r in range(len(shortest)):
            l, length = shortest[r]
            #  print('node %5d to landmark %5d = %5d steps' % (i, l, length))
            diff = reconstruct(G, paths[i][landmarks[l]])
            dist = np.linalg.norm(translation_angle_from_SE2(diff)[0])
            references[:, r] = Sl[:, l]
            distances[r] = dist
        S[:, i] = place(references, distances)
        
    results['Dl'] = Dl
    results['landmarks'] = landmarks
    results['landmarks_constraints'] = landmarks_constraints
    results['Sl'] = Sl
    results['S'] = S
        
    return results

def main():
    compmake.set_namespace('floyd_bench')
    filename = sys.argv[1]
    G = comp(load_graph, filename)     
    tc = dict(G=G,)
    results = comp(efpno2, tc)
    comp(write_report, tc, results, 'out/floyd_bench.html')
    compmake_console()
