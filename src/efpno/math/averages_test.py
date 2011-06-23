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


def pose_average_test_1():
    poses = [np.array([[ 0.94358775, 0.33112256, -0.70083654],
       [-0.33112256, 0.94358775, -0.4262584 ],
       [ 0.        , 0.        , 1.        ]]),
     np.array([[ 0.94485296, 0.32749486, -0.71541909],
       [-0.32749486, 0.94485296, -0.47418934],
       [ 0.        , 0.        , 1.        ]])]
    average = pose_average(poses, debug=True)
    
array = np.array

def pose_average_test_2():
    poses = [array([[ 0.9998629 , 0.01655842, -0.22509385],
       [-0.01655842, 0.9998629 , -4.0957236 ],
       [ 0.        , 0.        , 1.        ]]),
        array([[ 0.9998629 , 0.01655843, -0.22509666],
       [-0.01655843, 0.9998629 , -4.09572511],
       [ 0.        , 0.        , 1.        ]])]
    
    weights = [ 0.50932717, 0.49067283]
    pose_average(poses, weights, debug=True)
    
def pose_average_test_3():
    poses = [array([[-0.99882934, 0.04837305, -3.04662208],
       [-0.04837305, -0.99882934, -0.14072737],
       [ 0.        , 0.        , 1.        ]]), array([[-0.99882934, 0.04837306, -3.04662384],
       [-0.04837306, -0.99882934, -0.14073033],
       [ 0.        , 0.        , 1.        ]])]
    weights = [ 0.66712901, 0.33287099]
    pose_average(poses, weights, debug=True)

