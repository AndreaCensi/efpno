import sys
from efpno.script.loading import load_graph, smart_load
from efpno.parsing.write import graph_write
from optparse import OptionParser
import os
from reprep import Report
from efpno.report.report import report_add_coordinates_and_edges
from contracts.enabling import disable_all
from efpno.graphs.performance import graph_degree_stats

usage = """

    %cmd   [--outdir DIRECTORY]   [filename]  

    Other arguments:
        --fast  does not use contracts checks
""" 

def main():
    parser = OptionParser(usage=usage)

    parser.add_option("--outdir", default='.')
    
    parser.add_option("--fast", default=False, action='store_true',
                      help='Disables sanity checks.')
    

    (options, args) = parser.parse_args() #@UnusedVariable
    
    if options.fast:
        disable_all()
    
    if len(args) > 1:
        raise Exception('Too many arguments')
    
    filename = args[0] if args else 'stdin'
    G = smart_load(filename, raise_if_unknown=True, progress=True)

    print('Creating report...')
    r = create_report(G)
    
    rd = os.path.join(options.outdir, 'images')
    out = os.path.join(options.outdir, '%s.html' % G.graph['name'])
    print('Writing to %r' % out)
    r.to_html(out, resources_dir=rd)
    
    
def create_report(G):
    r = Report(G.graph['name'])
    f = r.figure()
    
    report_add_coordinates_and_edges(r, 'graph', G, f,
                                     plot_edges=True, plot_vertices=True)
    report_add_coordinates_and_edges(r, 'graph-edges', G, f,
                                     plot_edges=True, plot_vertices=False)
    report_add_coordinates_and_edges(r, 'graph-vertices', G, f,
                                     plot_edges=False, plot_vertices=True)
    
    r.text('stats', graph_degree_stats(G))
    return r



if __name__ == '__main__':
    main()
