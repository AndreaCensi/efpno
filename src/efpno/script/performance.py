import numpy as np

def constraints_and_observed_distances(G, S):
    d_c = []
    d_e = []
    for u, v in G.edges():
        d_c.append(G[u][v]['dist'])
        d_e.append(np.linalg.norm(S[:, u] - S[:, v]))
    d_c = np.array(d_c)
    d_e = np.array(d_e)
    err_eu = np.abs(d_c - d_e).mean()
    err_log = (np.log(d_c / d_e) ** 2).mean()
    return dict(d_c=d_c, d_e=d_e, err_eu=err_eu, err_log=err_log)
