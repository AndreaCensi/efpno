from ..math import SE2_to_distance, translation_angle_from_SE2, contract, np

def constraints_and_observed_distances(G, S):
    d_c = []
    d_e = []
    for u, v in G.edges():
        constraint = G[u][v]['dist']
        assert u != v
        assert constraint > 0
        d_c.append(constraint)
        d_e.append(np.linalg.norm(S[:, u] - S[:, v]))
    d_c = np.array(d_c)
    d_e = np.array(d_e)
    d = dict(d_c=d_c, d_e=d_e)
    d.update(**distances_metrics(d_c, d_e))
    return d

@contract(d_c='array[K](>0)', d_e='array[K](>0)')
def distances_metrics(d_c, d_e):
    err_flat = np.abs(d_c - d_e)
    err_log = np.abs(np.log(d_c / d_e))
    err_flat_mean = err_flat.mean()
    err_log_mean = err_log.mean()
                     
    return dict(distances_err_flat_max=err_flat.max(),
                distances_err_log_max=err_log.max(),
                distances_err_flat_mean=err_flat_mean,
                distances_err_log_mean=err_log_mean)

def distances_metrics_print(what, metrics):
    s = 'Metrics for %s:\n' % what
    s += (' - flat: max %10.3f mean %10.3f\n' % 
          (metrics['distances_err_flat_max'],
           metrics['distances_err_flat_mean']))
    s += (' -  log: max %10.3f mean %10.3f' % 
          (metrics['distances_err_log_max'],
           metrics['distances_err_log_mean']))
    return s

def graph_errors(constraints, solution):
    errors_t = []
    errors_theta = []
    if not constraints.edges():
        raise Exception('No edges in constraints graph.')
    
    d_c = []
    d_e = []
    
    for u, v in constraints.edges():
        assert u != v
        pose_u = solution.node[u]['pose']
        pose_v = solution.node[v]['pose']
        u_to_v = np.dot(np.linalg.inv(pose_u), pose_v)
        given = constraints[u][v]['pose']
        error = np.dot(np.linalg.inv(u_to_v), given)
        e_t, e_theta = translation_angle_from_SE2(error)
        errors_t.append(np.linalg.norm(e_t))
        errors_theta.append(np.abs(e_theta))
        
        # Distances error
        dist_constraint = constraints[u][v]['dist']
        assert dist_constraint > 0
        dist_estimated = SE2_to_distance(u_to_v) 
        assert dist_estimated > 0
        d_c.append(dist_constraint)
        d_e.append(dist_estimated)

    d_c = np.array(d_c)
    d_e = np.array(d_e)

    errors_t = np.array(errors_t)
    errors_theta = np.array(errors_theta)
    
    d = {}
    d['distances_constraints'] = d_c
    d['distances_estimated'] = d_e
    d.update(**distances_metrics(d_c, d_e))
    d['errors_t'] = errors_t
    d['errors_theta'] = errors_theta
    d['errors_t_mean'] = errors_t.mean() 
    d['errors_theta_mean'] = errors_theta.mean()
    d['errors_t_max'] = errors_t.max() 
    d['errors_theta_max'] = errors_theta.max()
    
    for s in ['errors_theta_max', 'errors_theta_mean']:
        d['%s_deg' % s] = np.degrees(d[s])
    return d

def graph_errors_print(what, d):
    s = 'Metrics for %s:\n' % what
    s += (' -      T: max %10.3f mean %10.3f\n' % 
          (d['errors_t_max'], d['errors_t_mean']))
    s += (' -  theta: max %10.3fdeg mean %10.3fdeg' % 
          (d['errors_theta_max_deg'], d['errors_theta_mean_deg']))
    return s


@contract(D_c='array[NxN](>=0)', D_e='array[NxN](>=0)')
def distances_matrix_metrics(D_c, D_e):
    n = D_c.shape[0]
    D_c = D_c.copy()
    D_e = D_e.copy()
    for i in range(n):
        D_c[i, i] = 1
        D_e[i, i] = 1
    return distances_metrics(np.array(D_c.flat), np.array(D_e.flat)) 




def graph_degree_stats(G):
    nodes = G.nodes()
    nodes_degree = np.array([len(G.neighbors(n)) for n in nodes], dtype='int32')
    max_degree = max(nodes_degree)
    
    stats = ""
    if 'name' in G.graph:
        stats += 'Graph name: %r  \n\n' % G.graph['name'] 
    stats += "Number of nodes: %s  \n\n" % G.number_of_nodes() 
    stats += "Number of edges: %s  \n\n" % G.number_of_edges()
    
    stats += "\nNode degrees ::\n\n"
    for d in range(max_degree + 1):
        num = (nodes_degree == d).sum()
        stats += ('    degree %3d: %6d nodes  \n' % (d, num))
    
    return stats     


def graph_degree_stats_compact(G):
    nodes = G.nodes()
    nodes_degree = np.array([len(G.neighbors(n)) for n in nodes], dtype='int32')
    max_degree = max(nodes_degree)
    
    stats = ""
    if 'name' in G.graph:
        stats += 'Graph name: %r  ' % G.graph['name'] 
    stats += "  nodes: %s " % G.number_of_nodes() 
    stats += "  edges: %s\n" % G.number_of_edges()
    
    num = "     #:  "
    deg = "degree:  "
    
    for d in range(min(max_degree + 1, 16)):
        deg += "%7d" % d
        n = (nodes_degree == d).sum()
        num += "%7d" % n
    stats += deg + '\n' + num + '\n'
    
        
    return stats     

