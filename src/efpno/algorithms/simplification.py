from ..graphs import (all_pairs_shortest_path, graph_errors, graph_errors_print)
from ..meat import (simplify_graph, reattach,
        solve_by_reduction, compute_fully_connected_subgraph)

from . import Algorithm       

class EFPNO_S(Algorithm):
    
    def solve(self, G):
        max_dist = self.params['max_dist']       
        results = {}  

        self.phase('compute:simplification')

        print('Loaded graph with %d nodes, %d edges.' % (G.number_of_nodes(),
                                                         G.number_of_edges()))

        landmarks_subgraph, how_to_reattach = simplify_graph(G, max_dist=max_dist)
    
        print('Reduced graph with %d nodes, %d edges.' % 
              (landmarks_subgraph.number_of_nodes(),
               landmarks_subgraph.number_of_edges()))

        self.phase('compute:shortest_paths')
        subpaths = all_pairs_shortest_path(landmarks_subgraph)

        self.phase('compute:fully_connect')
        landmarks_subgraph_full = \
            compute_fully_connected_subgraph(landmarks_subgraph, paths=subpaths) 

        self.phase('compute:solve_by_reduction')
        G_landmarks = solve_by_reduction(landmarks_subgraph_full)

        self.phase('compute:placing other nodes')
        print('G_landmarks: %s' % G_landmarks.nodes())
        G_all = reattach(G_landmarks, how_to_reattach)
            
        self.phase('stats:computing graph_errors')
        # note that this is a dense graph
        nlandmarks = landmarks_subgraph.number_of_nodes()
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
    
        self.phase('Done!')
        
        results['landmarks'] = landmarks_subgraph.nodes() 
        results['landmarks_subgraph'] = landmarks_subgraph
        return results

