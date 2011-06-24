from contracts import disable_all
from ..graphs import graph_degree_stats, graph_errors, graph_errors_print
from ..parsing import smart_load
from ..report import (report_add_coordinates_and_edges,
    report_add_distances_errors_plot)
from optparse import OptionParser
from reprep import Report
import os


usage = """

    %cmd   [--outdir DIRECTORY]   [filename]  

    Other arguments:
        --fast  does not use contracts checks
""" 

def main():
    parser = OptionParser(usage=usage)

    parser.add_option("--outdir", default='.')
    
    parser.add_option("--slow", default=False, action='store_true',
                      help='Enables sanity checks.')
    
    parser.add_option("--stats", default=False, action='store_true',
                      help='Computes statistics.')
    
    (options, args) = parser.parse_args() #@UnusedVariable
    
    if not options.slow:
        disable_all()
    
    if len(args) > 1:
        raise Exception('Too many arguments')
    
    filename = args[0] if args else 'stdin'
    G = smart_load(filename, raise_if_unknown=True, progress=True)

    print('Creating report...')
    r = create_report(G, options.stats)
    
    rd = os.path.join(options.outdir, 'images')
    out = os.path.join(options.outdir, '%s.html' % G.graph['name'])
    print('Writing to %r' % out)
    r.to_html(out, resources_dir=rd)
    
    
def create_report(G, constraint_stats=False):
    r = Report(G.graph['name'])
    f = r.figure("Graph plots")
    
    report_add_coordinates_and_edges(r, 'graph', G, f,
                                     plot_edges=True, plot_vertices=True)
    report_add_coordinates_and_edges(r, 'graph-edges', G, f,
                                     plot_edges=True, plot_vertices=False)
    report_add_coordinates_and_edges(r, 'graph-vertices', G, f,
                                     plot_edges=False, plot_vertices=True)
    
    
    r.text('node_statistics', graph_degree_stats(G))

    if constraint_stats:
        f = r.figure("Constraints statistics")
        print('Creating statistics')
        stats = graph_errors(G, G)
        print(' (done)')
        report_add_distances_errors_plot(r, nid='statistics', stats=stats, f=f)

        r.text('constraints_stats',
                graph_errors_print('constraints', stats))

    return r



if __name__ == '__main__':
    main()
