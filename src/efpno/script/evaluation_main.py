import itertools
import os

from compmake import comp, compmake_console, batch_command, use_filesystem
from contracts import disable_all
from optparse import OptionParser, OptionGroup

from ..math import np
from ..report import (create_report_tc, create_tables_for_paper,
    create_report_execution, create_report_comb_stats)
from .combinations import get_everything
from .wildcards import expand_string

    
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

    if len(which) == 1:    
        compmake_storage = os.path.join(options.outdir, 'compmake', which[0])
    else:
        compmake_storage = os.path.join(options.outdir, 'compmake', 'common_storage')
    
    use_filesystem(compmake_storage)


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

