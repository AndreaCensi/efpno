from reprep import Report
from contracts import contract
from geometry import assert_allclose
import numpy as np
from efpno.script.performance import constraints_and_observed_distances
from geometry.poses import translation_angle_from_SE2

def create_report_execution(exc_id,
                           tcid,
                           tc, algo_class, algo_params,
                          results):
    r = Report(exc_id)
     
    f = r.figure('misc') 
#    G = tc.G
    G_all = results.get('G_all', None)
    G_landmarks = results.get('G_landmarks', None)
    landmarks = np.array(results['landmarks'], dtype='int32')
    
#    Dl = results['Dl']
#    Sl = results['Sl']
#    S = results['S']
#    assert_allclose(G.number_of_nodes(), S.shape[1])
    
    if G_landmarks is not None: 
        print('plotting landmark positions %s' % G_landmarks.number_of_nodes())
        report_add_coordinates_and_edges(r, 'G_landmarks', G=G_landmarks,
                                          f=f, caption='landmarks positions')
    else:
        print("could not find G_landmarks")
        
    if G_all is not None: 
        print('plotting full solution %s' % G_all.number_of_nodes())
        report_add_coordinates_and_edges(r, 'G_all', G=G_all,
                                         landmarks=landmarks,
                                      f=f, caption='all nodes positions') 
    else:
        print("could not find G_all")
#    report_add_coordinates_and_edges(r, 'S_edges', S, G, f, 'all positions')
    
#    f1 = r.figure('sol1', cols=3)
#    print('plotting S')
#    report_add_solution(r=r, nid='stage1', S=S, G=G, landmarks=landmarks, f=f1)
#     
#    r.data('Dl', Dl).display('scale').add_to(f)
    
    return r
#
#    print('Writing to %r.' % filename)
#    r.to_html(filename)

def report_add_solution(r, nid, S, G, landmarks, f):
    print('%s: plotting edges' % nid)
    report_add_coordinates_and_edges(r=r, nid='%s_S' % nid,
                                     S=S, G=G, landmarks=landmarks, f=f,
                                     caption='positions') 
    
    print('%s: recomputing stats' % nid)
    stats = constraints_and_observed_distances(G, S)
#    print('%10s: eu: %10s  log: %10s' % (nid, stats['err_eu'],
#                                              stats['err_log']))

    print('%s: plotting stats' % nid)
    with r.data_pylab('%s_constrained_vs_estimated' % nid) as pylab:
        pylab.plot(stats['d_c'], stats['d_e'], '.')
        pylab.xlabel('constrained')
        pylab.ylabel('estimated')
        pylab.axis('equal')
        d = max([stats['d_e'].max(), stats['d_c'].max()])
        pylab.axis([0, d, 0, d])
        pylab.title('eu: %s  log: %s' % (stats['err_flat_mean'],
                                         stats['err_log_mean']))
    r.last().add_to(f)
    
    with r.data_pylab('%s_constrained_vs_estimated_log' % nid) as pylab:
        pylab.loglog(stats['d_c'], stats['d_e'], '.')
        pylab.xlabel('constrained')
        pylab.ylabel('estimated')
        pylab.title('log: %s' % (stats['err_log_mean']))

    r.last().add_to(f)
    
fs = 6
#
#@contract(S='array[2xN]')
#def report_add_coordinates(r, nid, S, f=None, caption=None):
#    with  r.data_pylab(nid, figsize=(fs, fs)) as pylab:
#        pylab.plot(S[0, :], S[1, :], 'r.')
#        pylab.axis('equal')
#    if f:
#        r.last().add_to(f, caption)

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
        pylab.plot(coords[0, :], coords[1, :], 'k.')
            
        if landmarks is not None:
            pylab.plot(coords[0, landmarks], coords[1, landmarks], 'r.')
        
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

#
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



def create_tables_for_paper(comb_id, tc_ids, alg_ids, deps):
    pass
 


def create_report_tc(tcid, tc):
    r = Report('test_case-%s' % tcid)
    return r

