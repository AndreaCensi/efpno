from contracts import contract
from . import se2_from_SE2, SE2_from_se2, np, SE2

@contract(poses='list[N](SE2),N>=1', weights='None|list[N](>=0)',
          start='None|SE2', iterations='int,>=1')
def pose_average(poses, weights=None, start=None, iterations=4):
    # TODO: make generic
    if start is None:
        start = poses[-1]
    
    N = len(poses)
    if weights is None:
        weights = [1.0 / N for pose in poses]
    
    center = poses[-1]
    for k in range(iterations):
        sum = np.zeros((3, 3))
        inv_center = np.linalg.inv(center)
        for pose, weight in zip(poses, weights):
            pz = np.dot(inv_center, pose)
            sum += se2_from_SE2(pz) * weight
        center = np.dot(center, SE2_from_se2(sum))
        if False:
            error = np.linalg.norm(sum)
            print('%3d: error: %20.12f  %s' % (k, error, SE2.friendly(center)))

    return center
        
    
    
    
