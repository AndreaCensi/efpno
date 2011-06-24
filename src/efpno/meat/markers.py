from contracts import contract
from ..math import direction, np, SE2_from_translation_angle
from geometry.basic_utils import assert_allclose

@contract(S='array[2xN]', returns='list(SE2)')
def markers2poses(S):
    K = S.shape[1]
    assert K % 3 == 0
    N = K / 3
    poses = []
    for i in range(N):
        A, B, C = i, i + N, i + 2 * N
        head = S[:, A]
        tail = 0.5 * (S[:, B] + S[:, C]) 
        theta = direction(tail, head)
        center = (S[:, A] + S[:, B] + S[:, C]) / 3.0
        node_pose = SE2_from_translation_angle(center, theta)
        poses.append(node_pose)
    return poses

@contract(poses='list[N](SE2)', returns='array[2x(3*N)]')
def poses2markers(poses, scale=1):
    Srel = np.zeros((3, 3))
    H = np.sqrt(3) / 4
    A = np.array([+H , 0])
    B = np.array([-H , +0.5])
    C = np.array([-H , -0.5])
    mean = (A + B + C) / 3
    A -= mean
    B -= mean
    C -= mean
    A *= scale
    B *= scale
    C *= scale
    
    # Make sure it is an equilateral triangle
    # of side "scale"
    dist = lambda x, y: np.linalg.norm(x - y)
    assert_allclose(dist(A, B), dist(B, C))
    assert_allclose(dist(B, C), dist(A, C))
    assert_allclose(dist(A, B), scale)
    assert_allclose((A + B + C) / 3, [0, 0])
    
    Srel[:, 0] = [A[0], A[1], 1]
    Srel[:, 1] = [B[0], B[1], 1]
    Srel[:, 2] = [C[0], C[1], 1]
    
    
    N = len(poses)
    S = np.zeros((2, 3 * N))
    for i, pose in enumerate(poses):
        markers = np.dot(pose, Srel)[:2, :]
        S[:, i + 0 * N] = markers[:, 0]
        S[:, i + 1 * N] = markers[:, 1]
        S[:, i + 2 * N] = markers[:, 2]
    return S

