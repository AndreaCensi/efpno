import sys
from efpno.script.loading import load_graph
from efpno.parsing.write import graph_write
from optparse import OptionParser
import os
from reprep import Report
from efpno.report.report import report_add_coordinates_and_edges
from contracts.enabling import disable_all

def main():
    parser = OptionParser()

    parser.add_option("--outdir", default='.')

    parser.add_option("--plot_edges", default=False)
    
    parser.add_option("--fast", default=False, action='store_true',
                      help='Disables sanity checks.')
    

    (options, args) = parser.parse_args() #@UnusedVariable
    
    if options.fast:
        disable_all()
    
    if not args: 
        fin = sys.stdin
        fname = 'stdin'
        sys.stderr.write('Reading from stdin...\n')
    else:
        filename = args[0]
        fin = open(filename)
        sys.stderr.write('Reading from %r...\n' % filename)
        fname = os.path.splitext(os.path.basename(filename))[0]
    
    G = load_graph(fin, raise_if_unknown=True, progress=True)

    print('Creating report...')
    r = create_report(G, plot_edges=options.plot_edges)
    
    out = os.path.join(options.outdir, '%s.html' % fname)
    print('Writing on %r' % out)
    r.to_html(out)
    
def create_report(G, plot_edges=False):
    r = Report()
    f = r.figure()
    
    report_add_coordinates_and_edges(r, 'graph', G, f,
                                     plot_edges=True, plot_vertices=True)
    report_add_coordinates_and_edges(r, 'graph-edges', G, f,
                                     plot_edges=True, plot_vertices=False)
    report_add_coordinates_and_edges(r, 'graph-vertices', G, f,
                                     plot_edges=False, plot_vertices=True)
    
    return r

if __name__ == '__main__':
    main()
