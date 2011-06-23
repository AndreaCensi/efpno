from ..math import SE2_from_translation_angle, pose_diff, np 
from . import DiGraph

import itertools
import sys

def grid_graph(nrows=30, ncols=30, every=1, side=1):
    ''' Creates a grid graph. '''
    G = DiGraph()
    coords2node = {}
    
    def get_node(coords):

        if not coords in coords2node:
            k = len(coords2node)
            theta = np.random.uniform(0, 2 * np.pi)
            t = [coords[0] * side, coords[1] * side]
            pose = SE2_from_translation_angle(t, theta)
            G.add_node(k, pose=pose)
            coords2node[coords] = k 
        return coords2node[coords]
        
    def connect(c1, c2):
        u = get_node(c1)
        v = get_node(c2)
        pose_u = G.node[u]['pose']
        pose_v = G.node[v]['pose']
        u_to_v = pose_diff(pose_u, pose_v)
        v_to_u = np.linalg.inv(u_to_v)
        G.add_edge(u, v, pose=u_to_v, weight=1.0)
        G.add_edge(v, u, pose=v_to_u, weight=1.0)
        
    for i, j in itertools.product(range(nrows), range(ncols)):
        if i > 0 and (j % every == 0): 
            connect((i, j), (i - 1, j)) # up
        if j > 0 and i % every == 0: 
            connect((i, j), (i, j - 1)) # left
        
    return G

def main():
    usage = """
    Creates grid graph.
    """

    from optparse import OptionParser
    from efpno.parsing.write import graph_write
    parser = OptionParser(usage=usage)

    parser.add_option("--outdir", default='.')
    
    parser.add_option("--nrows", default=30, type="int")
    parser.add_option("--ncols", default=30, type="int")
    parser.add_option("--side", default=1, type="int")
    parser.add_option("--every", default=1, type="int")

    (options, args) = parser.parse_args() #@UnusedVariable

    G = grid_graph(options.nrows, options.ncols, options.every, side=options.side)
    graph_write(G, sys.stdout)
    
    
    

