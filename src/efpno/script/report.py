from reprep import Report
from contracts import contract
from geometry import assert_allclose
import numpy as np
from efpno.script.performance import constraints_and_observed_distances

def create_report_execution(exc_id,
                           tcid,
                           tc, algo_class, algo_params,
                          results):
    r = Report(exc_id)
     
    f = r.figure('misc') 
    G = tc.G
    Dl = results['Dl']
    Sl = results['Sl']
    landmarks = np.array(results['landmarks'], dtype='int32')
    S = results['S']
    assert_allclose(G.number_of_nodes(), S.shape[1])
    
    print('plotting landmark positions')
    report_add_coordinates_and_edges(r, 'Sl', Sl, G, f, 'landmarks positions') 
     
#    report_add_coordinates_and_edges(r, 'S_edges', S, G, f, 'all positions')
    
    f1 = r.figure('sol1', cols=3)
    print('plotting S')
    report_add_solution(r=r, nid='stage1', S=S, G=G, landmarks=landmarks, f=f1)
    
    if 'S2' in results:
        S2 = results['S2']
        report_add_solution(r=r, nid='stage2', S=S2, G=G, f=f1)
#    for k in range(4):
#        var = 'S%d' % k
#        report_add_solution(r, var, results[var], G, f1)

    
    r.data('Dl', Dl).display('scale').add_to(f)
    
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

@contract(S='array[2xN]')
def report_add_coordinates_and_edges(r, nid, S, G,
                                     f=None, caption=None,
                                     plot_edges=False,
                                     landmarks=None):
    with  r.data_pylab(nid, figsize=(fs, fs)) as pylab:
        pylab.plot(S[0, :], S[1, :], 'k.')
        if landmarks is not None:
            pylab.plot(S[0, landmarks], S[1, landmarks], 'r.')
        
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

