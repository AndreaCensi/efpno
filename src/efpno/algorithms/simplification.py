from ..graphs import (all_pairs_shortest_path, graph_errors, graph_errors_print, DiGraph)

from ..meat import (simplify_graph_aggressive, reattach,
        solve_by_reduction, compute_fully_connected_subgraph)

from . import Algorithm       

class EFPNO_S(Algorithm):
    
    def solve(self, G):
        max_dist = self.params['max_dist']       
        results = {}  

        self.info('Loaded graph with %d nodes, %d edges.' % (G.number_of_nodes(),
                                                         G.number_of_edges()))

        self.phase('compute:simplification')
        landmarks_subgraph, how_to_reattach = \
            simplify_graph_aggressive(G, max_dist=max_dist,
                                      eprint=self.info, min_nodes=200)
    
        self.info('Reduced graph with %d nodes, %d edges.' % 
              (landmarks_subgraph.number_of_nodes(),
               landmarks_subgraph.number_of_edges()))

        self.phase('compute:shortest_paths')
        subpaths = all_pairs_shortest_path(landmarks_subgraph)

        self.phase('compute:fully_connect')
        landmarks_subgraph_full = \
            compute_fully_connected_subgraph(landmarks_subgraph, paths=subpaths) 

        self.phase('compute:solve_by_reduction')
        G_landmarks = solve_by_reduction(landmarks_subgraph_full, scale=1,
                                         eprint=self.info)

        self.phase('compute:placing other nodes')
        self.info('G_landmarks: %s' % G_landmarks.nodes())
        G_all = reattach(G_landmarks, how_to_reattach)
            
        
        solution = DiGraph(G)
        for x in G.nodes():
            solution.node[x]['pose'] = G_all.node[x]['pose']
            
        self.phase('stats:computing graph_errors')
        # note that this is a dense graph
        nlandmarks = landmarks_subgraph.number_of_nodes()
        if nlandmarks < 100:
            lgstats = graph_errors(constraints=landmarks_subgraph,
                                   solution=G_landmarks)
            self.info(graph_errors_print('landmark-gstats', lgstats))
            results['lgstats'] = lgstats

        gstats = graph_errors(constraints=solution, solution=solution)

        self.phase('debug:printing')
        
        
        self.info(graph_errors_print('all-gstats', gstats))

        
        results['G_all'] = G_all
        results['G_landmarks'] = G_landmarks
        results['solution'] = solution
        results['gstats'] = gstats
    
        self.phase('Done!')
        
        results['landmarks'] = landmarks_subgraph.nodes() 
        results['landmarks_subgraph'] = landmarks_subgraph
        return results

