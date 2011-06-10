from . import translation_angle_from_SE2, np, SE2_from_translation_angle

def area(a, b, c):
    M = np.ones((3, 3))
    M[0, :2] = a
    M[1, :2] = b
    M[2, :2] = c
    return np.linalg.det(M)

def direction(tail, head):
    v = head - tail
    return np.arctan2(v[1], v[0])

def SE2_to_distance(g): # TODO: make more efficient
    t = translation_angle_from_SE2(g)[0]
    return np.linalg.norm(t)

def random_SE2(max_t=10, max_theta=np.pi):
    t = np.random.uniform(-1, 1, 2) * max_t
    theta = np.random.uniform(-1, 1) * max_theta
    return SE2_from_translation_angle(t, theta)

def pose_diff(u, v):
    ''' u * pose_diff(u,v) = v '''
    # TODO: remove inverse
    return np.dot(np.linalg.inv(u), v)
