from geometry import mds, place
from geometry import euclidean_distances

from efpno.script.utils import reconstruct, SE2_to_distance, area, direction
import numpy as np
import networkx as nx #@UnresolvedImport
from networkx import  single_source_shortest_path, all_pairs_shortest_path #@UnresolvedImport

from efpno.script.performance import  distances_matrix_metrics, \
    distances_metrics_print, constraints_and_observed_distances, graph_errors, \
    graph_errors_print
import itertools
from geometry.basic_utils import assert_allclose
from geometry.poses import SE2_from_translation_angle
import time
from geometry.manifolds import SE2
from contracts.main import contract
from efpno.script.markers import poses2markers, markers2poses
from geometry.mds import mds_randomized

class Algorithm:
    def __init__(self, params):
        self.params = params
        self.phases = []
        self.current_phase = None
        
    def solve_main(self, tc):
        G = tc.G
        results = self.solve(G)
        self.phase('done')
        
        self.print_phase_details()
        
        def add_to_main(main, d, prefix):
            for k, v in d.items():
                main['%s-%s' % (prefix, k)] = v
    
        add_to_main(results, results.get('lstats', {}), 'landmarks-relstats')
        add_to_main(results, results.get('stats', {}), 'all-relstats')
        add_to_main(results, results.get('lgstats', {}), 'landmarks-gstats')
        add_to_main(results, results.get('gstats', {}), 'all-gstats')
        results['phases'] = self.phases
        return results
    
    def phase(self, name):
        if self.current_phase:
            prev, t0 = self.current_phase
            t1 = time.clock()
            self.phases.append((prev, t1 - t0))
            
        self.current_phase = (name, time.clock())
        
        print(name)
    
    def print_phase_details(self):
        print('Benchmarks:')
        for phase, t in self.phases:
            print('- %10d ms -- %s ' % (t * 1000, phase))
            
    def progress(self, what, i, n):
        if i % 20 == 0:
            print('%s: %5d/%d' % (what, i, n))
        
class EFPNO3(Algorithm):
    def solve(self, G):
        nl = self.params['nl']
        nref = self.params['nref']  
        lmode = self.params['lmode'] 
        multi = self.params.get('multi', False)
        improve = self.params.get('improve', False)
      
        n = G.number_of_nodes()
        freq = int(np.ceil(n / nl))
        landmarks = range(0, n, freq)
        nlandmarks = len(landmarks)
#        ndim = 2
        results = {}  

#        dijkstra_path(G,source,target, weight = 'weight'):
        
        self.phase('compute:shortest_path')
        paths = {}
        for i, l in enumerate(landmarks):
            self.progress('single source shortest path', i, nlandmarks)
            paths[l] = single_source_shortest_path(G, l) 
        
        print('Using %d landmarks for %d nodes.' % (nlandmarks, n))
        
        self.phase('compute:computing subgraph')
        landmarks_subgraph = compute_subgraph(G, paths, landmarks)
        
        if lmode == 'euclidean':
            self.phase('solving euclidean')
            G2, Sl, Dl = solve_euclidean(landmarks_subgraph)
            self.phase('computing metric for landmarks')
            Sl_d = euclidean_distances(Sl)
            lstats = distances_matrix_metrics(Dl, Sl_d)
            print(distances_metrics_print('landmark-relstats', lstats))
            results['lstats'] = lstats
            S = place_other_nodes(G, paths, landmarks, Sl, nref)
            results['S'] = S
        
            self.phase('computing stats')
            stats = constraints_and_observed_distances(G, S)
            print(distances_metrics_print('all-relstats', stats))
            results['stats'] = stats
            results['Dl'] = Dl
            results['Sl'] = Sl

        elif lmode == 'reduce':
        
            self.phase('compute:solve_by_reduction')
            G_landmarks = solve_by_reduction(landmarks_subgraph)

            self.phase('compute:placing other nodes')
            if multi:
                G_all = place_other_nodes_multi(G=G, paths=paths,
                                             landmarks=landmarks,
                                             landmarks_solution=G_landmarks)
            else:
                G_all = place_other_nodes_simple(G=G, paths=paths,
                                             landmarks=landmarks,
                                             landmarks_solution=G_landmarks)
            if improve:
                self.phase('compute:improvement')
                G_all = improve_guess(G, G_all)
                
            self.phase('stats:computing graph_errors')
            # note that this is a dense graph
            if False:
                lgstats = graph_errors(constraints=landmarks_subgraph,
                                       solution=G_landmarks)
                print(graph_errors_print('landmark-gstats', lgstats))
                results['lgstats'] = lgstats

            gstats = graph_errors(constraints=G, solution=G_all)

            self.phase('debug:printing')
            
            
            print(graph_errors_print('all-gstats', gstats))

            
            results['G_all'] = G_all
            results['G_landmarks'] = G_landmarks
            results['gstats'] = gstats
        
        else: raise Exception('unknown lmode %r' % lmode)
        
    
        self.phase('Done!')
        
        results['landmarks'] = landmarks
        results['landmarks_subgraph'] = landmarks_subgraph
        return results

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

    G2 = nx.DiGraph()
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
    
def solve_by_reduction(G, scale=1):
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
    
    G2 = nx.DiGraph() 
    print('solve_by_reduction: marker to pose')
    poses = markers2poses(Sall)
    it2node = G.nodes()
    for i, pose in enumerate(poses):
        G2.add_node(it2node[i], pose=pose)
    return G2


def compute_subgraph(G, paths, landmarks, node_ids=None, add_self=False):
    S = nx.DiGraph()
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

def place_other_nodes_simple(G, paths, landmarks, landmarks_solution):
    nlandmarks = len(landmarks)
    n = G.number_of_nodes()
    
    G2 = nx.DiGraph()
    for i in range(n):
        i_to_landmarks = [(l, len(paths[landmarks[l]][i])) 
                          for l in range(nlandmarks)]
        l = sorted(i_to_landmarks, key=lambda x:x[1])[0][0]
        diff = reconstruct(G, paths[landmarks[l]][i])
        landmark_pose = landmarks_solution.node[l]['pose']
        pose = np.dot(landmark_pose, diff)
        
        G2.add_node(i, pose=pose)
    return G2 


from networkx import subgraph #@UnresolvedImport

def place_other_nodes_multi(G, paths, landmarks, landmarks_solution):
    nlandmarks = len(landmarks)
    n = G.number_of_nodes()
    
    G2 = nx.DiGraph()
    
    landmark_group = {}
    for l in range(nlandmarks):
        landmark_group[l] = []
        
    for i in range(n):
        i_to_landmarks = [(l, len(paths[landmarks[l]][i])) 
                          for l in range(nlandmarks)]
        l_closest_to_i = sorted(i_to_landmarks, key=lambda x:x[1])[0][0]
        landmark_group[l_closest_to_i].append(i)
    
    for l in range(nlandmarks):
        landmark_pose = landmarks_solution.node[l]['pose']
        nchildren = len(landmark_group[l])
        print('Landmark %d has %d children' % (l, nchildren))
        # a landmark is always its own child
        if nchildren == 1:
            G2.add_node(landmark_group[l][0], pose=landmark_pose)
            continue
        if nchildren == 0: continue

        nodes = landmark_group[l] + [landmarks[l]]
        Gsub = subgraph(G, nodes) 
        
        Gsub_solution = solve_dense(Gsub, fix_node=landmarks[l],
                              fix_pose=landmark_pose)
        
        for i in landmark_group[l]:
            G2.add_node(i, pose=Gsub_solution.node[i]['pose'])
        
    return G2 

def assert_same_nodes(G1, G2):
    if set(G2.nodes()) != set(G1.nodes()):
        s = 'G1: %s\nG2: %s' % (sorted(G1.nodes()), sorted(G2.nodes())) 
        
        raise Exception(s)

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
#                    
#        for i, j in itertools.product(range(n), range(n)):
#            if np.isfinite(D_constraints[i, j]):
#                D[i, j] = D_constraints[i, j]
#                
#        assert_allclose(D2, D, atol=1e-8)
        print('MDS')
        S = mds_randomized(D2, 2)
        print('Distances')
        D = euclidean_distances(S)
    
        change = np.abs(D - D0).mean()
        print('Mean change: %f' % change)
        
    poses = markers2poses(S)
    
    G2 = nx.DiGraph()
    for i, u in enumerate(nodes):
        G2.add_node(u, pose=poses[i])
    return G2 

