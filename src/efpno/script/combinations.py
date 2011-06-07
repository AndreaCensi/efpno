from efpno.script.efpno2 import EFPNO3
from efpno.script.loading import load_log_tc
from collections import namedtuple

Combination = namedtuple('Combination', 'algorithms test_cases')

# algorithms, logs, sets = get_everything(

def get_everything():
    
    algorithms = [
        ('Efast', (EFPNO3, dict(nref=3, nl=48, lmode='euclidean'))),
        ('EfastR', (EFPNO3, dict(nref=3, nl=48, lmode='reduce'))),
        ('Eslow', (EFPNO3, dict(nref=3, nl=100, lmode='euclidean'))),
        ('EslowR', (EFPNO3, dict(nref=3, nl=100, lmode='reduce')))

    ]
    
    logs = [
        ('intel', (load_log_tc, dict(filename='data/intel.g2o'))),
        ('man3500', (load_log_tc, dict(filename='data/manhattanOlson3500.g2o'))),
    ]
    
    sets = {}
    
    sets['tmp'] = Combination(['Efast*'], '*')
    
    sets['all'] = Combination('*', '*')
    
    return dict(algorithms), dict(logs), sets
