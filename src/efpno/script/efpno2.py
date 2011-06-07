from geometry import mds, place
from geometry import euclidean_distances

from efpno.script.utils import reconstruct, SE2_to_distance
import numpy as np
import networkx as nx #@UnresolvedImport
from networkx import  single_source_shortest_path #@UnresolvedImport

from efpno.script.performance import  distances_matrix_metrics, \
    distances_metrics_print, constraints_and_observed_distances, graph_errors, \
    graph_errors_print
import itertools
from geometry.basic_utils import assert_allclose
from geometry.poses import SE2_from_translation_angle

class Algorithm:
    def __init__(self, params):
        self.params = params

    def solve_main(self, tc):
        G = tc.G
        results = self.solve(G)

        def add_to_main(main, d, prefix):
            for k, v in d.items():
                main['%s-%s' % (prefix, k)] = v
    
        add_to_main(results, results.get('lstats', {}), 'landmarks-relstats')
        add_to_main(results, results.get('lgstats', {}), 'landmarks-gstats')
        add_to_main(results, results.get('stats', {}), 'all-relstats')
        
        print ' %.4f\n'.join(results.keys())
        return results
    
    def phase(self, name):
        print(name)
    def progress(self, what, i, n):
        if i % 100 == 0:
            print('%s: %5d/%d' % (what, i, n))
        
class EFPNO3(Algorithm):
    def solve(self, G):
        nl = self.params['nl']
        nref = self.params['nref']  
        lmode = self.params['lmode'] 
      
        n = G.number_of_nodes()
        freq = int(np.ceil(n / nl))
        landmarks = range(0, n, freq)
        nlandmarks = len(landmarks)
        ndim = 2
        results = {}  

        self.phase('shortest_path')
        paths = {}
        for i, l in enumerate(landmarks):
            self.progress('single source shortest path', i, nlandmarks)
            paths[l] = single_source_shortest_path(G, l) 
        
        print('Using %d landmarks for %d nodes.' % (nlandmarks, n))
        
        self.phase('computing subgraph')
        landmarks_subgraph = compute_subgraph(G, paths, landmarks)
        
        if lmode == 'euclidean':
            self.phase('solving euclidean')
            G2, Sl, Dl = solve_euclidean(landmarks_subgraph)
            self.phase('computing metric for landmarks')
        elif lmode == 'reduce':
            G2, Sl, Dl, Sall, Dall = solve_by_reduction(landmarks_subgraph)
            lgstats = graph_errors(constraints=landmarks_subgraph, solution=G2)
            print(graph_errors_print('landmark-gstats', lgstats))
            results['lgstats'] = lgstats
        else: raise Exception('unknown lmode %r' % lmode)
        
        Sl_d = euclidean_distances(Sl)
        lstats = distances_matrix_metrics(Dl, Sl_d)
    
        print(distances_metrics_print('landmark-relstats', lstats))
        
        self.phase('Putting other nodes')
        S = place_other_nodes(G, paths, landmarks, Sl, nref)
       
        
        self.phase('computing stats')
        stats = constraints_and_observed_distances(G, S)
        print(distances_metrics_print('all-relstats', stats))

        self.phase('Done!')
        
        results['Dl'] = Dl
        results['landmarks'] = landmarks
        results['landmarks_subgraph'] = landmarks_subgraph
        results['Sl'] = Sl
        results['S'] = S
        results['lstats'] = lstats
#        results['lgstats'] = lgstats
        results['stats'] = stats
        return results

def extract_distances(G):
    n = G.number_of_nodes()
    D = np.zeros((n, n))
    for i, j  in itertools.product(range(n), range(n)):
        D[i, j] = G[i][j]['dist']
        if i == j:
            assert_allclose(D[i, j], 0)
        else:
            assert D[i, j] > 0, D[i, j]
    return D

def solve_euclidean(G):
    D = extract_distances(G) 
    S = mds(D, 2)

    G2 = nx.DiGraph()
    n = G.number_of_nodes()
    for i in range(n):    
#        u = G.neighbours(i)[0]
#        constraint = G[i][u]['pose']
        theta = 0
        node_pose = SE2_from_translation_angle(S[:, i], theta) 
        G2.add_node(i, pose=node_pose)
    return G2, S, D

def solve_by_reduction(G, scale=1):
    n = G.number_of_nodes()
    Dall = np.ones((3 * n, 3 * n)) * np.NaN
    Srel = np.zeros((3, 3))
    Srel[:, 0] = [0, 0, 1] * scale
    Srel[:, 1] = [-1, 0.5, 1] * scale
    Srel[:, 2] = [-1, -0.5, 1] * scale
    
    for i, j  in itertools.product(range(n), range(n)):
        pose = G[i][j]['pose']
        Sset = np.zeros((2, 6))
        Sset[:, 0:3] = Srel[:2, :]
        Sset[:, 3:6] = np.dot(pose, Srel)[:2, :]
        Dset = euclidean_distances(Sset)
        indices = [i, i + n, i + 2 * n, j, j + n, j + 2 * n]
        for u, v in itertools.product(range(6), range(6)):
            Dall[indices[u], indices[v]] = Dset[u, v]

    Sall = mds(Dall, 2)
    
    G2 = nx.DiGraph()
#    G2 = nx.DiGraph(G)
    def area(a, b, c):
        M = np.ones((3, 3))
        M[0, :2] = a
        M[1, :2] = b
        M[2, :2] = c
        return np.linalg.det(M)
    
    areas = np.zeros(n)
    for i in range(n):
        areas[i] = area(Sall[:, i], Sall[:, i + n], Sall[:, i + 2 * n])
        
        #print('Area of %s: %d  %f ' % (i, s, A))
#    print('Average area: %s' % areas.mean())
    if np.mean(np.sign(areas)) < 0:
#        print('Seems like the solution is flipped; adjusting.')
        Sall[0, :] = -Sall[0, :]
    else:
        pass
#        print('Solution has correct orientation.')
    
    for i in range(n):
        head = Sall[:, i]
        tail = 0.5 * (Sall[:, i + n] + Sall[:, i + 2 * n])
        d = np.linalg.norm(head - tail)
#        print('%d  head-tail: %10.4f' % (i, d))
        theta = direction(tail, head)
        node_pose = SE2_from_translation_angle(head, theta) 
        G2.add_node(i, pose=node_pose)
        
    S = Sall[:n, :n]
    D = Dall[:n, :n]
    return G2, S, D, Dall, Sall

def direction(tail, head):
    v = head - tail
    return np.arctan2(v[1], v[0])

def compute_subgraph(G, paths, landmarks):
    S = nx.DiGraph()
    nlandmarks = len(landmarks)
    for i in range(nlandmarks):
#                self.progress('l2l distances', i, nlandmarks)
        for j in range(nlandmarks):
            u, v = landmarks[i], landmarks[j]
            pose = reconstruct(G, paths[u][v])
            dist = SE2_to_distance(pose)
            S.add_edge(i, j, pose=pose, dist=dist)
            
    for i in range(nlandmarks):
        dist = S[i][i]['dist']
        assert_allclose(dist, 0)
#            v_to_u = reconstruct(G, paths[u][v][::-1]) 
#            assert_inverse(u_to_v, v_to_u)
    return S
    
 
def place_other_nodes(G, paths, landmarks, Sl, nref):
    ndim = 2
    nlandmarks = len(landmarks)
    n = G.number_of_nodes()
    
    S = np.zeros((ndim, n))
    for i in range(n):
#                self.progress('placing other nodes', i, n)
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
    return S

class EFPNO2(Algorithm):
    def solve(self, G):
        pass
