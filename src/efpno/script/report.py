from reprep import Report
from contracts import contract
from geometry import assert_allclose
import numpy as np
from efpno.script.performance import constraints_and_observed_distances, \
    graph_errors_print
from geometry.poses import translation_angle_from_SE2

def create_report_execution(exc_id,
                           tcid,
                           tc, algo_class, algo_params,
                          results):
    r = Report(exc_id)
     
    f = r.figure('misc', cols=3) 
    
    for w in ['gstats', 'lgstats']:
        r.text(w, graph_errors_print(w, results[w]))

    G = tc.G
    landmarks = results['landmarks']
    
    G_all = results.get('G_all', None)
    G_landmarks = results.get('G_landmarks', None)
    lgstats = results.get('lgstats', None)
    
    if G_landmarks is not None: 
        print('plotting landmark positions %s' % G_landmarks.number_of_nodes())
        report_add_coordinates_and_edges(r, 'G_landmarks', G=G_landmarks,
                                          f=f, caption='landmarks positions')
        
        if  lgstats is not None:
            report_add_distances_errors_plot(r, nid='lgstats', stats=lgstats, f=f)
    else:
        print("could not find G_landmarks")
    
    for u, v in G.edges():
        G_all.add_edge(u, v, **G[u][v]) 
    if G_all is not None: 
        print('plotting full solution %s' % G_all.number_of_nodes())
        report_add_coordinates_and_edges(r, 'G_all', G=G_all,
                                         landmarks=landmarks,
#                                         plot_edges=True,
                                      f=f, caption='all nodes positions') 
        report_add_distances_errors_plot(r, nid='gstats', stats=results['gstats'], f=f)
    else:
        print("could not find G_all") 
    return r 

def report_add_distances_errors_plot(r, nid, stats, f):
    d_c = stats['distances_constraints']
    d_e = stats['distances_estimated']
    
    with r.data_pylab('%s-flat' % nid) as pylab:
        pylab.plot(d_c, d_e, '.')
        pylab.xlabel('constrained')
        pylab.ylabel('estimated')
        pylab.axis('equal')
        d = max([d_c.max(), d_e.max()])
        pylab.axis([0, d, 0, d])
    
    r.last().add_to(f)
    
    with r.data_pylab('%s-log' % nid) as pylab:
        pylab.loglog(d_c, d_e, '.')
        pylab.xlabel('constrained')
        pylab.ylabel('estimated')
    
    r.last().add_to(f)
#
#def report_add_solution(r, nid, S, G, landmarks, f):
#    print('%s: plotting edges' % nid)
#    report_add_coordinates_and_edges(r=r, nid='%s_S' % nid,
#                                     S=S, G=G, landmarks=landmarks, f=f,
#                                     caption='positions') 
#    
#    print('%s: recomputing stats' % nid)
#    stats = constraints_and_observed_distances(G, S) 
#
#    print('%s: plotting stats' % nid)
#    with r.data_pylab('%s_constrained_vs_estimated' % nid) as pylab:
#        pylab.plot(stats['d_c'], stats['d_e'], '.')
#        pylab.xlabel('constrained')
#        pylab.ylabel('estimated')
#        pylab.axis('equal')
#        d = max([stats['d_e'].max(), stats['d_c'].max()])
#        pylab.axis([0, d, 0, d])
#        pylab.title('eu: %s  log: %s' % (stats['err_flat_mean'],
#                                         stats['err_log_mean']))
#    r.last().add_to(f)
#    
#    with r.data_pylab('%s_constrained_vs_estimated_log' % nid) as pylab:
#        pylab.loglog(stats['d_c'], stats['d_e'], '.')
#        pylab.xlabel('constrained')
#        pylab.ylabel('estimated')
#        pylab.title('log: %s' % (stats['err_log_mean']))
#
#    r.last().add_to(f)
#    
fs = 9

def get_coords(G):
    n = G.number_of_nodes()
    coords = np.zeros((2, n))
    for u in G.nodes():
        t, angle = translation_angle_from_SE2(G.node[u]['pose'])
        coords[:, u] = t
    return coords

def report_add_coordinates_and_edges(r, nid, G,
                                     f=None, caption=None,
                                     plot_edges=False,
                                     landmarks=None):
    coords = get_coords(G)
    
    with r.data_pylab(nid, figsize=(fs, fs)) as pylab:
        style = {}
        pylab.plot(coords[0, :], coords[1, :], 'k.', **style)
            
        if landmarks is not None:
            pylab.plot(coords[0, landmarks], coords[1, landmarks], 'rx',
                       **style)
        
        if plot_edges:
            for u, v in G.edges():
                d_c = G[u][v]['dist']
                d_o = np.linalg.norm(coords[:, u] - coords[:, v])
                if d_o < d_c:
                    color = 'r-'
                else:
                    color = 'b-'
                     
                pylab.plot([ coords[0, u], coords[0, v] ],
                           [ coords[1, u], coords[1, v] ], color)
            
        pylab.axis('equal')
    if f is not None:
        r.last().add_to(f, caption)



def create_tables_for_paper(comb_id, tc_ids, alg_ids, deps):
    pass
 
def create_report_tc(tcid, tc):
    r = Report('test_case-%s' % tcid)
    return r

