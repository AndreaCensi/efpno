from geometry import translation_angle_from_SE2


def graph_write(G, f,
                 vertex_command='VERTEX_XYT',
                 edge_command='EDGE_XYT', endline='\n'):
    for u in G.nodes():
        pose = G.node[u]['pose']
        t, theta = translation_angle_from_SE2(pose)
        f.write('%s %d %f %f %f %s' % 
                (vertex_command, u, t[0], t[1], theta, endline))
        
    for u, v in G.edges():
        if u > v: continue
        diff = G[u][v]['pose']
        t, theta = translation_angle_from_SE2(diff)
        f.write('%s %d %d %f %f %f %s' % 
                (edge_command, u, v, t[0], t[1], theta, endline))
