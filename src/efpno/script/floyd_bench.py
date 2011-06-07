import networkx as nx
from efpno.parsing.parse import parse
import sys
from efpno.parsing.structures import AddVertex2D, AddEdge2D
import time
import compmake
from reprep import Report
from geometry import mds, place
from geometry import SE2
from geometry import translation_angle_from_SE2
from contracts.main import contract
from geometry import euclidean_distances
from geometry.basic_utils import assert_allclose
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
    G = nx.DiGraph()
    raise_if_unknown = True
    count = 0
    with open(filename) as f:
        for x in parse(f, raise_if_unknown=raise_if_unknown):
            if isinstance(x, AddVertex2D):
                G.add_node(int(x.id))
                
            if isinstance(x, AddEdge2D):
                G.add_edge(int(x.id1), int(x.id2), pose=x.pose, inf=x.inf,
                            dist=SE2_to_distance(x.pose))
                G.add_edge(int(x.id2), int(x.id1), pose=SE2.inverse(x.pose), inf=x.inf,
                           dist=SE2_to_distance(x.pose))
        
            if count % 100 == 0:
                print count
            count += 1
    check_proper(G)
    return G

def assert_inverse(pose1, pose2):
    d = SE2.multiply(pose1, pose2)
    assert_allclose(d, np.eye(3), atol=1e-8,
                     err_msg='Diff: %s' % SE2.friendly(d))
    
    
def check_proper(G):
    for u, v in G.edges():
        pose1 = G[u][v]['pose']
        pose2 = G[v][u]['pose']
        assert_inverse(pose1, pose2)
from networkx.algorithms.shortest_paths.dense import *
 
     
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

from compmake import comp, compmake_console
import numpy as np

def constraints_and_observed_distances(G, S):
    true = []
    seen = []
    for u, v in G.edges():
        true.append(G[u][v]['dist'])
        seen.append(np.linalg.norm(S[:, u] - S[:, v]))
    return np.array(true), np.array(seen)

def write_report(tc, results, filename):
    r = Report()
     
    f = r.figure('misc') 
    G = tc['G']
    Dl = results['Dl']
    Sl = results['Sl']
    S = results['S']
    assert_allclose(G.number_of_nodes(), S.shape[1])
    
    print('plotting landmark positions')
    report_add_coordinates(r, 'Sl', Sl, f, 'landmarks positions') 
     
#    report_add_coordinates_and_edges(r, 'S_edges', S, G, f, 'all positions')
    
    f1 = r.figure('sol1', cols=2)
    print('plotting S')
    report_add_solution(r, 'stage1', S, G, f1)
    
#    S2 = results['S2']
    
#    report_add_solution(r, 'stage2', S2, G, f1)
#    for k in range(4):
#        var = 'S%d' % k
#        report_add_solution(r, var, results[var], G, f1)
#    
#    report_add_coordinates(r, 'S', S, f1, 'positions') 
#    d_c, d_e = constraints_and_observed_distances(G, S)
#    with r.data_pylab('constrained_vs_estimated') as pylab:
#        pylab.plot(d_c, d_e, '.')
#        pylab.xlabel('constrained')
#        pylab.ylabel('estimated')
#    r.last().add_to(f1)
#    
    r.data('Dl', Dl).display('scale').add_to(f)
    
    print('Writing to %r.' % filename)
    r.to_html(filename)

def report_add_solution(r, nid, S, G, f):
    report_add_coordinates_and_edges(r, '%s_S' % nid, S, G, f, 'positions') 
    d_c, d_e = constraints_and_observed_distances(G, S)
    err_eu = np.abs(d_c - d_e).mean()
    err_log = (np.log(d_c / d_e) ** 2).mean()
    print('%10s: eu: %10s  log: %10s' % (nid, err_eu, err_log))
    with r.data_pylab('%s_constrained_vs_estimated' % nid) as pylab:
        pylab.plot(d_c, d_e, '.')
        pylab.xlabel('constrained')
        pylab.ylabel('estimated')
        pylab.title('eu: %s  log: %s' % (err_eu, err_log))
    r.last().add_to(f)
    
fs = 6
@contract(S='array[2xN]')
def report_add_coordinates(r, nid, S, f=None, caption=None):
    with  r.data_pylab(nid, figsize=(fs, fs)) as pylab:
        pylab.plot(S[0, :], S[1, :], 'r.')
        pylab.axis('equal')
    if f:
        r.last().add_to(f, caption)

@contract(S='array[2xN]')
def report_add_coordinates_and_edges(r, nid, S, G, f=None, caption=None,
                                     plot_edges=False):
    with  r.data_pylab(nid, figsize=(fs, fs)) as pylab:
        pylab.plot(S[0, :], S[1, :], 'k.')
        
        if plot_edges:
            for u, v in G.edges():
                d_c = G[u][v]['dist']
                d_o = np.linalg.norm(S[:, u] - S[:, v])
                if d_o < d_c:
                    color = 'r-'
                else:
                    color = 'b-'
                     
                pylab.plot([ S[0, u], S[0, v] ],
                           [ S[1, u], S[1, v] ], color)
            
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
        edge_pose = edge['pose']
        pose = np.dot(pose, edge_pose)
#        pose = np.dot(edge_pose, pose)
    return pose


def efpno2(tc):
    G = tc['G']
    n = G.number_of_nodes()
    print('Number of nodes: %d' % n)
#    freq = 10
    nl = 300
    freq = int(np.ceil(n / nl))
    landmarks = range(0, n, freq)
    
    ndim = 2
    results = {}  
    print('all_pairs_shortest_path')
    paths = {}
    for l in landmarks:
#        print('single source %d' % l)
        paths[l] = single_source_shortest_path(G, l)
  
#    paths = timeit(all_pairs_shortest_path, G) #@UndefinedVariable
    
    nref = 5
    
    nlandmarks = len(landmarks)
    print('Using landmarks: %s' % nlandmarks)
    print('Using landmarks: %s' % landmarks)
    landmarks_constraints = {}
    Dl = np.zeros((nlandmarks, nlandmarks))
    for i in range(nlandmarks):
        landmarks_constraints[i] = {}
        if i % 10 == 0: print('i=%d/%d' % (i, nlandmarks))
        for j in range(nlandmarks):
            u = landmarks[i]
            v = landmarks[j]
            u_to_v = reconstruct(G, paths[u][v])
#            v_to_u = reconstruct(G, paths[u][v][::-1])
#            print paths[u][v]
#            print paths[v][u]
#            assert_inverse(u_to_v, v_to_u)
            Dl[i, j] = SE2_to_distance(u_to_v)
            landmarks_constraints[i][j] = u_to_v
    print('Solving MDS')
    Sl = mds(Dl, ndim)
    Sl_d = euclidean_distances(Sl)
    landmark_rel_error = np.abs(Dl - Sl_d).mean()
    print('Landmark relative error: %s' % landmark_rel_error)
    
    print('Putting other')
    S = np.zeros((ndim, n))
    for i in range(n):
        if i % 100 == 0: print(' i=%d ' % i)
        i_to_landmarks = [(l, len(paths[landmarks[l]][i])) 
                          for l in range(nlandmarks)]

        shortest = sorted(i_to_landmarks, key=lambda x:x[1])[:nref]
        references = np.zeros((ndim, nref))
        distances = np.zeros(nref)
        for r in range(len(shortest)):
            l, length = shortest[r]
            #  print('node %5d to landmark %5d = %5d steps' % (i, l, length))
            diff = reconstruct(G, paths[landmarks[l]][i])
            references[:, r] = Sl[:, l]
            distances[r] = SE2_to_distance(diff)
        S[:, i] = place(references, distances)
        
    results['Dl'] = Dl
    results['landmarks'] = landmarks
    results['landmarks_constraints'] = landmarks_constraints
    results['Sl'] = Sl
    results['S'] = S
        
    return results

def stage2(tc, results):
    G = tc['G']
    S_old = results['S']
    for k in range(5):
        print('K=%d ' % k)
        D = euclidean_distances(S_old)
        for u, v in G.edges():
            d_c = G[u][v]['dist']
            D[u, v] = d_c 
            D[v, u] = d_c
        print('  mds')
        S_new = mds(D, 2)
        results['S%d' % k] = S_new
        S_old = S_new
        
    results['S2'] = S_new
    return results 
    

def main():
    compmake.set_namespace('floyd_bench')
    filename = sys.argv[1]
    G = comp(load_graph, filename)     
    tc = dict(G=G,)
    results = comp(efpno2, tc)
#    results = comp(stage2, tc, results)
    
    comp(write_report, tc, results, 'out/floyd_bench.html')
    compmake_console()
