from . import SE2, assert_allclose, np

def assert_inverse(pose1, pose2): # TODO: make more efficient
    d = SE2.multiply(pose1, pose2)
    assert_allclose(d, np.eye(3), atol=1e-8,
                     err_msg='Diff: %s' % SE2.friendly(d))
     
