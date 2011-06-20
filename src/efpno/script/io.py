import sys
from efpno.script.loading import load_graph
from efpno.parsing.write import graph_write

def main():
    fin = sys.stdin
    fout = sys.stdout
    G = load_graph(fin, raise_if_unknown=True, progress=True)
    graph_write(G, fout)

if __name__ == '__main__':
    main()
