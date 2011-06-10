import time
        
def timeit(func, *args, **kwargs):
    t0 = time.clock()
    res = func(*args, **kwargs)
    t1 = time.clock()
    cpu = t1 - t0
    print('%s(%s,%s): %s ms' % (func.__name__, args, kwargs, 1000 * cpu))
    return res

    

