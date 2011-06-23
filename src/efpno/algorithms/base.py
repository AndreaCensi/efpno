import time
import sys

class Algorithm:
    def __init__(self, params):
        self.params = params
        self.phases = []
        self.current_phase = None
        
    def solve_main(self, tc):
        G = tc.G
        results = self.solve(G)
        self.phase('done')
        
        self.print_phase_details()
        
        def add_to_main(main, d, prefix):
            for k, v in d.items():
                main['%s-%s' % (prefix, k)] = v
    
        add_to_main(results, results.get('lstats', {}), 'landmarks-relstats')
        add_to_main(results, results.get('stats', {}), 'all-relstats')
        add_to_main(results, results.get('lgstats', {}), 'landmarks-gstats')
        add_to_main(results, results.get('gstats', {}), 'all-gstats')
        results['phases'] = self.phases
        results['phases_as_text'] = Algorithm.get_phase_desc(self.phases)
        return results
    
    def phase(self, name):
        if self.current_phase:
            prev, t0 = self.current_phase
            t1 = time.clock()
            self.phases.append((prev, t1 - t0))
            
        self.current_phase = (name, time.clock())
        
        if name is not None:
            self.info('Phase %s' % name)
    
    @staticmethod
    def get_phase_desc(phases):
        s = ''
        for phase, t in phases:
            s += ('- %10d ms -- %s \n' % (t * 1000, phase))
        return s
        
    def print_phase_details(self):
        self.info('Benchmarks:')
        self.info(Algorithm.get_phase_desc(self.phases))
            
    def progress(self, what, i, n):
        if i % 20 == 0:
            self.info('%s: %5d/%d' % (what, i, n))
 
    def info(self, s):
        # TODO: logger
        sys.stderr.write(s)
        sys.stderr.write('\n')
        
        
