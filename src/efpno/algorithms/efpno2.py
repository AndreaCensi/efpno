from ..math import np, euclidean_distances
from ..graphs import (
      single_source_shortest_path, distances_matrix_metrics,
      distances_metrics_print, constraints_and_observed_distances, graph_errors,
    graph_errors_print)
from ..meat import (
        compute_subgraph, place_other_nodes, place_other_nodes_multi,
        place_other_nodes_simple, place_other_nodes_mref, solve_euclidean,
        solve_by_reduction, improve_guess)

from . import Algorithm       
       
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
                if nref == 1:
                    G_all = place_other_nodes_simple(G=G, paths=paths,
                                             landmarks=landmarks,
                                             landmarks_solution=G_landmarks)
                else:
                    G_all = place_other_nodes_mref(G=G, paths=paths,
                                                   landmarks=landmarks,
                                                   landmarks_solutions=G_landmarks, nref=nref)
#            self.phase('compute:sparse constraints')
#            Dsparse = markers_constraints_sparse(G)
                
            if improve:
                self.phase('compute:improvement')
                G_all = improve_guess(G, G_all)
                
            self.phase('stats:computing graph_errors')
            # note that this is a dense graph
            if nlandmarks < 100:
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

