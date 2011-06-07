import networkx as nx
import sys
import compmake
from geometry import mds, place
from geometry import euclidean_distances
from compmake import comp, compmake_console
import numpy as np

from efpno.script.utils import reconstruct, SE2_to_distance
from efpno.script.loading import load_graph
from efpno.script.report import write_report

from networkx import  single_source_shortest_path

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
    results = comp(stage2, tc, results)
    comp(write_report, tc, results, 'out/floyd_bench.html')
    compmake_console()
