from reprep import Report
from ..math import translation_angle_from_SE2
from ..graphs import  graph_errors_print


def create_report_execution(exc_id,
                           tcid,
                           tc, algo_class, algo_params,
                          results):
    r = Report(exc_id)
     
    f = r.figure('misc', cols=3) 
    
    for w in ['gstats', 'lgstats']:
        if w in results:
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
    
        
    if G_all is not None: 
        for u, v in G.edges():
            G_all.add_edge(u, v, **G[u][v]) 
        print('plotting full solution %s' % G_all.number_of_nodes())
        report_add_coordinates_and_edges(r, 'G_all', G=G_all,
                                         landmarks=landmarks,
#                                         plot_edges=True,
                                      f=f, caption='all nodes positions') 
        report_add_distances_errors_plot(r, nid='gstats', stats=results['gstats'], f=f)
    else:
        print("could not find G_all")
        
    r.text('phases_as_text', results['phases_as_text']) 
    return r 

def report_add_distances_errors_plot(r, nid, stats, f):
    d_c = stats['distances_constraints']
    d_e = stats['distances_estimated']
    
    with r.plot('%s-flat' % nid) as pylab:
        pylab.plot(d_c, d_e, '.')
        pylab.xlabel('constrained')
        pylab.ylabel('estimated')
        pylab.axis('equal')
        d = max([d_c.max(), d_e.max()])
        pylab.axis([0, d, 0, d])
    
    r.last().add_to(f)
    
    with r.plot('%s-log' % nid) as pylab:
        pylab.loglog(d_c, d_e, '.')
        pylab.xlabel('constrained')
        pylab.ylabel('estimated')
    
    r.last().add_to(f)
fs = 9


def get_coord(G, x):
    t, angle = translation_angle_from_SE2(G.node[x]['pose']) #@UnusedVariable
    return t

def report_add_coordinates_and_edges(r, nid, G,
                                     f=None, caption=None,
                                     plot_edges=True,
                                     plot_vertices=True,
                                     vertex_style=dict(color='r', alpha=0.5),
                                     edge_style=dict(color='k', alpha=0.5)):

    with r.plot(nid, figsize=(fs, fs)) as pylab:
        if plot_edges:
            xends = []
            yends = []
            for u, v in G.edges():
                c_u = get_coord(G, u)
                c_v = get_coord(G, v) 
                xends.extend([c_u[0], c_v[0]])
                xends.append(None)
                yends.extend([c_u[1], c_v[1]])
                yends.append(None)
            pylab.plot(xends, yends, '-', **edge_style)
        
        if plot_vertices:
            x = []; y = []
            for u in G.nodes():
                t = get_coord(G, u)
                x.append(t[0])
                y.append(t[1])
            pylab.plot(x, y, '.', **vertex_style)
        
        pylab.axis('equal')

    if f is not None:
        r.last().add_to(f, caption)



def create_tables_for_paper(comb_id, tc_ids, alg_ids, deps):
    pass
 
def create_report_tc(tcid, tc):
    r = Report('test_case-%s' % tcid)
    return r

