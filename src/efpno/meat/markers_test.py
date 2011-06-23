from ..math import  SE2
from ..graphs import random_SE2_distribution
from . import poses2markers, markers2poses

def markers_test_1():
    N = 10
    for scale in [1, 10, 0.1]:
        poses1 = random_SE2_distribution(N)
        markers = poses2markers(poses1, scale=scale)
        poses2 = markers2poses(markers)
        
        for i in range(N):
            SE2.assert_close(poses1[i], poses2[i])
