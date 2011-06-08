from geometry.poses import SE2_from_translation_angle
from contracts.main import contract
from efpno.script.utils import direction
import numpy as np

@contract(S='array[2xN]', returns='list(SE2)')
def markers2poses(S):
    K = S.shape[1]
    assert K % 3 == 0
    N = K / 3
    poses = []
    for i in range(N):
        head = S[:, i]
        tail = 0.5 * (S[:, i + N] + S[:, i + 2 * N]) 
        theta = direction(tail, head)
        node_pose = SE2_from_translation_angle(head, theta)
        poses.append(node_pose)
    return poses

@contract(poses='list[N](SE2)', returns='array[2x(3*N)]')
def poses2markers(poses, scale=1):
    Srel = np.zeros((3, 3))
    Srel[:, 0] = [0, 0, 1] * scale
    Srel[:, 1] = [-1, 0.5, 1] * scale
    Srel[:, 2] = [-1, -0.5, 1] * scale
    N = len(poses)
    S = np.zeros((2, 3 * N))
    for i, pose in enumerate(poses):
        markers = np.dot(pose, Srel)[:2, :]
        S[:, i + 0 * N] = markers[:, 0]
        S[:, i + 1 * N] = markers[:, 1]
        S[:, i + 2 * N] = markers[:, 2]
    return S

