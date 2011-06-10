from efpno.script.efpno2 import EFPNO3
from efpno.script.loading import load_log_tc
from collections import namedtuple

Combination = namedtuple('Combination', 'algorithms test_cases')

# algorithms, logs, sets = get_everything(

def get_everything():
    
    algorithms = [
#        ('Efast', (EFPNO3, dict(nref=3, nl=50, lmode='euclidean'))),
        ('E-L10-R1', (EFPNO3, dict(nref=1, nl=10, lmode='reduce'))),
        ('E-L10-R3', (EFPNO3, dict(nref=3, nl=10, lmode='reduce'))),
        ('E-L25-R1', (EFPNO3, dict(nref=1, nl=25, lmode='reduce'))),
        ('E-L25-R3', (EFPNO3, dict(nref=3, nl=25, lmode='reduce'))),
        ('E-L50-R1', (EFPNO3, dict(nref=1, nl=50, lmode='reduce'))),
        ('E-L50-R3', (EFPNO3, dict(nref=3, nl=50, lmode='reduce'))),
#        ('E25R', (EFPNO3, dict(nref=1, nl=25, lmode='reduce', multi=False))),
#        ('EfastR', (EFPNO3, dict(nref=3, nl=50, lmode='reduce', multi=False))),
##        ('EfastRi', (EFPNO3, dict(nref=3, nl=48, lmode='reduce', multi=False, improve=True))),
##        ('EfastRm', (EFPNO3, dict(nref=3, nl=48, lmode='reduce', multi=True))),
##        ('Eslow', (EFPNO3, dict(nref=3, nl=100, lmode='euclidean'))),
#        ('EslowR', (EFPNO3, dict(nref=3, nl=100, lmode='reduce', multi=False))),
##        ('EslowRm', (EFPNO3, dict(nref=3, nl=100, lmode='reduce', multi=True))),
#        ('EslugR', (EFPNO3, dict(nref=3, nl=150, lmode='reduce', multi=False))),
        
    ]
    
    logs = [
        ('intel', (load_log_tc, dict(filename='data/intel.g2o'))),
        ('man3500', (load_log_tc, dict(filename='data/manhattanOlson3500.g2o'))),
    ]
    
    sets = {}
    
    sets['intel'] = Combination(['E-L*-R*'], 'intel')
#    sets['tmp2'] = Combination(['EfastR'], 'intel')
#
#    sets['tmp3'] = Combination(['EslugR'], 'man3500')
    
    sets['all'] = Combination('*', '*')
    
    return dict(algorithms), dict(logs), sets
