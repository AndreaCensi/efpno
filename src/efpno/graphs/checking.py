from ..math import pose_diff, SE2, assert_inverse

def assert_exact(G):
    for u, v in G.edges():
        pose_u = G.node[u]['pose']
        pose_v = G.node[v]['pose']
        u_to_v = pose_diff(pose_u, pose_v)
        found = G[u][v]['pose']
        SE2.assert_close(u_to_v, found) 

   
def assert_well_formed(G):
    '''
        Graphs we use are:
    
        - no self edge
        - if u->v, then v->u
    '''
    for u, v in G.edges():
        if u == v:
            raise Exception('Found self-edge for node %s' % u)
        pose1 = G[u][v]['pose']
        pose2 = G[v][u]['pose']
        assert_inverse(pose1, pose2)


def assert_same_nodes(G1, G2):
    if set(G2.nodes()) != set(G1.nodes()):
        s = 'G1: %s\nG2: %s' % (sorted(G1.nodes()), sorted(G2.nodes())) 
        
        raise Exception(s)
