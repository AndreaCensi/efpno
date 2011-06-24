import sys
from ..parsing import graph_write
from .loading import load_graph

def main():
    fin = sys.stdin
    fout = sys.stdout
    G = load_graph(fin, raise_if_unknown=True, progress=True)
    graph_write(G, fout)

if __name__ == '__main__':
    main()
