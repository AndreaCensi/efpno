from geometry import SE2_from_xytheta
import numpy as np
from efpno.parsing.structures import AddVertex2D
from geometry.manifolds import SE2

def main():
    
    L = 10
    nside = 10
    k = 0
    
    poses = []
    def add_pose(x, y, theta):
        p = SE2_from_xytheta([x, y, theta])
        poses.append(p)
        
    for x in np.linspace(0, L, nside):
        add_pose(x, 0, 0)
    for y in np.linspace(0, L, nside):
        add_pose(L, y, np.pi / 2)
    for x in np.linspace(0, L, nside)[::-1]:
        add_pose(x, L, -np.pi / 2)
    for y in np.linspace(0, L, nside)[::-1]:
        add_pose(L, y, np.pi)
    
    cmds = []
    
    for i in range(len(poses)):
        cmds.append(AddVertex2D('%s' % i, None))
        
    for i in range(len(poses)):
        j = (i + 1) % len(poses)
        p_i = poses[i]  
        p_j = poses[j]
        diff = SE2.
        inf = np.identity(3)
        
    
