from efpno.script.efpno_test import random_SE2_distribution
from efpno.script.markers import poses2markers, markers2poses
from numpy.ma.testutils import assert_almost_equal

def markers_test_1():
    N = 10
    poses1 = random_SE2_distribution(N)
    markers = poses2markers(poses1)
    poses2 = markers2poses(markers)
    
    for i in range(N):
        assert_almost_equal(poses1[i], poses2[i])
