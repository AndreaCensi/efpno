from efpno.math import random_SE2, np, pose_average, SE2 


def pose_average_test():
    g = random_SE2(max_t=10)
    poses = []
    for i in range(3):
        h = random_SE2(max_t=1, max_theta=np.pi / 2)
        h_inv = np.linalg.inv(h)
        poses.append(np.dot(g, h)) 
        poses.append(np.dot(g, h_inv))
    average = pose_average(poses, iterations=15)
    diff = np.dot(np.linalg.inv(g), average)
    print('g1: %s' % SE2.friendly(g))
    print('g2: %s' % SE2.friendly(average))
    print('delta: %s' % SE2.friendly(diff))
    SE2.assert_close(g, average)
