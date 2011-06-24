from contracts import contract
from . import se2_from_SE2, SE2_from_se2, np, SE2
import sys
from geometry.basic_utils import assert_allclose

@contract(poses='list[N](SE2),N>=1', weights='None|seq[N](>=0)',
          start='None|SE2', iterations='int,>=1')
def pose_average(poses, weights=None, start=None, iterations=100, debug=False):
    # TODO: make generic
    if start is None:
        start = poses[-1]
    
    N = len(poses)
    if weights is None:
        weights = [1.0 / N for pose in poses]
    
    assert_allclose(np.sum(weights), 1, err_msg='Sum must be 1')
    
    center = poses[-1]
    for k in range(iterations):
        sum = np.zeros((3, 3))
        inv_center = np.linalg.inv(center)
        for pose, weight in zip(poses, weights):
            pz = np.dot(inv_center, pose)
            sum += se2_from_SE2(pz) * weight
        center = np.dot(center, SE2_from_se2(sum))
        error = np.linalg.norm(sum)
        if debug:
            sys.stderr.write('%3d: error: %20.12f  %s\n' % (k, error, SE2.friendly(center)))

        if error < 1e-8: break
    else:  
#        sys.stderr.write('%3d: error: %20.12f \n' % (k, error))
        msg = 'Could not converge after %d iterations.\n' % k
        msg += '\n poses =' + poses.__repr__()
        msg += '\n weights =' + weights.__repr__()
        raise Exception(msg)

#    sys.stderr.write('%3d: error: %20.12f \n' % (k, error))
    
    return center
        
    
    
    
