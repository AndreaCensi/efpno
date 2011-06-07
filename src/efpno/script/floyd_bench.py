import networkx as nx #@UnresolvedImport
import os
import itertools
from geometry import mds, place
from geometry import euclidean_distances
from compmake import comp, compmake_console, batch_command

from efpno.script.utils import reconstruct, SE2_to_distance

from efpno.script.report import (create_report_tc, create_tables_for_paper,
                                 create_tables_for_paper,
                                 create_report_execution)

from .tables import create_report_comb_stats

from networkx import  single_source_shortest_path #@UnresolvedImport
from optparse import OptionParser, OptionGroup
from contracts import disable_all
import numpy as np
from .combinations import get_everything
from .wildcards import expand_string

def efpno2(tc):
    G = tc['G']
    n = G.number_of_nodes()
    print('Number of nodes: %d' % n)
#    freq = 10
    nl = 300
    freq = int(np.ceil(n / nl))
    landmarks = range(0, n, freq)
    
    ndim = 2
    results = {}  
    print('all_pairs_shortest_path')
    paths = {}
    for l in landmarks:
#        print('single source %d' % l)
        paths[l] = single_source_shortest_path(G, l) 
    nref = 5
    
    nlandmarks = len(landmarks)
    print('Using landmarks: %s' % nlandmarks)
    print('Using landmarks: %s' % landmarks)
    landmarks_constraints = {}
    Dl = np.zeros((nlandmarks, nlandmarks))
    for i in range(nlandmarks):
        landmarks_constraints[i] = {}
        if i % 10 == 0: print('i=%d/%d' % (i, nlandmarks))
        for j in range(nlandmarks):
            u = landmarks[i]
            v = landmarks[j]
            u_to_v = reconstruct(G, paths[u][v])
#            v_to_u = reconstruct(G, paths[u][v][::-1])
#            print paths[u][v]
#            print paths[v][u]
#            assert_inverse(u_to_v, v_to_u)
            Dl[i, j] = SE2_to_distance(u_to_v)
            landmarks_constraints[i][j] = u_to_v
    print('Solving MDS')
    Sl = mds(Dl, ndim)
    Sl_d = euclidean_distances(Sl)
    landmark_rel_error = np.abs(Dl - Sl_d).mean()
    print('Landmark relative error: %s' % landmark_rel_error)
    
    print('Putting other')
    S = np.zeros((ndim, n))
    for i in range(n):
        if i % 100 == 0: print(' i=%d ' % i)
        i_to_landmarks = [(l, len(paths[landmarks[l]][i])) 
                          for l in range(nlandmarks)]

        shortest = sorted(i_to_landmarks, key=lambda x:x[1])[:nref]
        references = np.zeros((ndim, nref))
        distances = np.zeros(nref)
        for r in range(len(shortest)):
            l, length = shortest[r]
            #  print('node %5d to landmark %5d = %5d steps' % (i, l, length))
            diff = reconstruct(G, paths[landmarks[l]][i])
            references[:, r] = Sl[:, l]
            distances[r] = SE2_to_distance(diff)
        S[:, i] = place(references, distances)
        
    results['Dl'] = Dl
    results['landmarks'] = landmarks
    results['landmarks_constraints'] = landmarks_constraints
    results['Sl'] = Sl
    results['S'] = S
        
    return results

def stage2(tc, results):
    G = tc['G']
    S_old = results['S']
    for k in range(5):
        print('K=%d ' % k)
        D = euclidean_distances(S_old)
        for u, v in G.edges():
            d_c = G[u][v]['dist']
            D[u, v] = d_c 
            D[v, u] = d_c
        print('  mds')
        S_new = mds(D, 2)
        results['S%d' % k] = S_new
        S_old = S_new
        
    results['S2'] = S_new
    return results 
    
def main():
    parser = OptionParser()

    group = OptionGroup(parser, "Files and directories")

    group.add_option("--outdir",
                      help='Directory with variables.pickle and where '
                           'the output will be placed.')
    
    parser.add_option_group(group)

    group = OptionGroup(parser, "Experiments options")

    group.add_option("--fast", default=False, action='store_true',
                      help='Disables sanity checks.')
    
    group.add_option("--set", default='*',
                      help='[= %default] Which combinations to run.')

    group.add_option("--seed", default=None, type='int',
                      help='[= %default] Seed for random number generator.')
    
    parser.add_option_group(group)

    group = OptionGroup(parser, "Compmake options")

    group.add_option("--remake", default=False, action='store_true',
                      help='Remakes all (non interactive).')

    group.add_option("--report", default=False, action='store_true',
                      help='Cleans and redoes all reports (non interactive).')

    group.add_option("--report_stats", default=False, action='store_true',
                      help='Cleans and redoes the reports for the stats. (non interactive)')

    parser.add_option_group(group)

    (options, args) = parser.parse_args() #@UnusedVariable
    
    
    np.random.seed(options.seed)    
    
    if options.fast:
        disable_all()

    assert not args 
    assert options.outdir is not None 
    
    available_algorithms, available_test_cases, available_sets = get_everything()    
    
    which = expand_string(options.set, list(available_sets.keys()))

    print('Staging creation of test cases reports')
    test_cases = {}
    test_case_reports = {} 
    def stage_test_case_report(tcid):
        if not tcid in available_test_cases:
            msg = ('Could not find test case %r \n %s' % 
                   (tcid, available_test_cases.keys()))
            raise Exception(msg)
        if not tcid in test_cases:
            command, args = available_test_cases[tcid]
            job_id = 'test_case_data-%s' % tcid
            test_cases[tcid] = comp(command, job_id=job_id, **args)
        
        if not tcid in  test_case_reports:
            job_id = 'test_case-%s-report' % tcid
            report = comp(create_report_tc,
                          tcid, test_cases[tcid], job_id=job_id)
            job_id += '-write'
            filename = os.path.join(options.outdir, 'test_cases', '%s.html' % tcid)
            comp(write_report, report, filename, job_id=job_id)
            test_case_reports[tcid] = report
        return test_case_reports[tcid]
    
    # set of tuple (algo, test_case)
    executions = {}
    def stage_execution(tcid, algid):
        stage_test_case_report(tcid)
        
        key = (tcid, algid)
        if not key in executions:
            test_case = test_cases[tcid]
            algo_class, algo_params = available_algorithms[algid]
            job_id = 'solve-%s-%s-run' % (tcid, algid)
            results = comp(run_combination, tcid,
                           test_case, algo_class, algo_params,
                            job_id=job_id)
            executions[key] = results
            
            exc_id = '%s-%s' % (tcid, algid)
            # Create iterations report
            job_id = 'solve-%s-report' % exc_id
            report = comp(create_report_execution, exc_id,
                           tcid,
                           test_case, algo_class, algo_params,
                          results, job_id=job_id)
            
            job_id += '-write'
            filename = os.path.join(options.outdir, 'executions',
                                    '%s-%s.html' % (tcid, algid))
            comp(write_report, report, filename, job_id=job_id)
            
        return executions[key]
     
    
    for comb_id in which:
        comb = available_sets[comb_id]
        alg_ids = expand_string(comb.algorithms, available_algorithms.keys())
        tc_ids = expand_string(comb.test_cases, available_test_cases.keys())
        
        print('Set %r has %d test cases and %d algorithms (~%d jobs in total).' % 
          (comb_id, len(alg_ids), len(tc_ids), len(alg_ids) * len(tc_ids) * 2))

        deps = {}
        for t, a in itertools.product(tc_ids, alg_ids):
            deps[(t, a)] = stage_execution(t, a)

        job_id = 'tex-%s' % comb_id
        comp(create_tables_for_paper, comb_id, tc_ids, alg_ids, deps,
             job_id=job_id)
        
        job_id = 'set-%s-report' % comb_id
        report = comp(create_report_comb_stats,
                      comb_id, tc_ids, alg_ids, deps, job_id=job_id)
        
        job_id += '-write'
        filename = os.path.join(options.outdir, 'stats', '%s.html' % comb_id)
        comp(write_report, report, filename, job_id=job_id)

    if options.report or options.report_stats:
        if options.report:
            batch_command('clean *-report*')
        elif options.report_stats:
            batch_command('clean set-*  tex*')
        batch_command('parmake')
    elif options.remake:
        batch_command('clean *')
        batch_command('make set-* tex-*')
    else:
        compmake_console()


def write_report(report, filename):
    print('Writing report %r to %r.' % (report.id, filename))
    rd = os.path.join(os.path.dirname(filename), 'images')
    report.to_html(filename, resources_dir=rd)


def run_combination(tcid, tc, algo_class, algo_params):
    tc.tcid = tcid
    print('Running %s - %s(%s)' % (tcid, algo_class.__name__, algo_params))
    algo = algo_class(algo_params)
    results = algo.solve_main(tc)
    
    other = {'algo_class': algo_class,
             'combid': '%s-%s' % (tc.tcid, algo),
             'tcid': tcid }
    
    results.update(other)
    return results

