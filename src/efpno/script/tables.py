import numpy as np

from reprep import Report

natsorted = sorted # XXX

entries = """
all-gstats-errors_t_mean %.4f                                                                                           
all-gstats-errors_theta_mean_deg %.2fdeg                                                                                   
all-gstats-errors_t_max %.4f                                                                                            
all-gstats-errors_theta_max_deg %.4fdeg                                                                                    
landmarks-gstats-errors_t_mean %.4f                                                                                           
landmarks-gstats-errors_theta_mean_deg %.2fdeg                                                                                   
landmarks-gstats-errors_t_max %.4f                                                                                            
landmarks-gstats-errors_theta_max_deg %.4fdeg                                                                                    
landmarks-relstats-err_log_max %.4f                                                                                           
landmarks-relstats-err_log_mean %.4f                                                                                          
landmarks-relstats-err_flat_max %.4f    
landmarks-relstats-err_flat_mean %.4f                                                                                              
all-relstats-err_log_max %.4f                                                                                                 
all-relstats-err_log_mean %.4f                                                                                                
all-relstats-err_flat_max %.4f                                                                                                
all-relstats-err_flat_mean %.4f  
""".split('\n')
entries = [tuple(s.split()) for s in entries if s.split()]

def create_report_comb_stats(comb_id, tc_ids, alg_ids, deps):
    r = Report('set-%s' % comb_id)
    
#    has_ground_truth = 'cheat' in alg_ids or 'echeat' in alg_ids
#    
#    if 'cheat' in alg_ids: cheater = 'cheat'
#    if 'echeat' in alg_ids: cheater = 'echeat'
#     
#    if has_ground_truth:
#        for tc_id in tc_ids:
#            max_spearman = deps[(tc_id, cheater)]['spearman']
#            for alg_id in alg_ids:
#                res = deps[(tc_id, alg_id)]
#                res['spearman_score'] = res['spearman'] / max_spearman
    
    def tablevar(var, format='%.2f', not_found=np.NaN):
        def getter(tc_id, alg_id):
            res = deps[(tc_id, alg_id)]
            if var in res:
                return format % res[var]
            else:
                return not_found
        return getter

    print entries
    for var, format in entries:
        caption = var
        r.table(var, caption=caption,
            **generic_table(tc_ids, alg_ids, tablevar(var, format)))
        
    return r
    
def generic_table(tc_ids, alg_ids, get_element, sorted=True, mark_lower=True):
    if sorted:
        tc_ids = natsorted(tc_ids)
        alg_ids = natsorted(alg_ids)
    
    rows = tc_ids
    cols = alg_ids
    
    def make_row(tc_id):
        entries = [ get_element(tc_id, alg_id) for alg_id in alg_ids ]
#        if mark_lower:
#            # re-convert two numbers
#            # do not consider these for the stats:
#            avoid = ['rand2d', 'rand3d', 'cheat', 'echeat']
#            values = [float(x) for (algo, x) in zip(alg_ids, entries)]
#            selected = [float(x) for (algo, x) in zip(alg_ids, entries)
#                        if algo not in avoid]
#            values_max = max(selected)
#            values_min = min(selected)
#            for i in range(len(entries)):
#                if alg_ids[i] in avoid: continue 
#                if values[i] == values_max:
#                    mark = '(H)'
#                elif values[i] == values_min:
#                    mark = '(L)'
#                else:
#                    mark = None
#                if mark:
#                    entries[i] = '%s %s' % (mark, entries[i])
                    
        return entries 
    
    data = [make_row(tc_id) for tc_id in tc_ids] 
     
    return dict(data=data, rows=rows, cols=cols)        


