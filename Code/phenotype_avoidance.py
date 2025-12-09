
from pyboolnet.control_strategies import compute_control_strategies_with_model_checking, compute_control_strategies_with_completeness
from pyboolnet.repository import get_primes

# Define Phenotypes

E1 = [{"AJ_b1":1, "AJ_b2": 1, "FA_b1": 0, "FA_b2": 0, "FA_b3": 0}]
H1 = [{"AJ_b1":1, "AJ_b2": 1, "FA_b1": 1, "FA_b2": 0, "FA_b3": 0}]
H2 = [{"AJ_b1":1, "AJ_b2": 0, "FA_b1": 1, "FA_b2": 1, "FA_b3": 0}]
H3 = [{"AJ_b1":1, "AJ_b2": 1, "FA_b1": 1, "FA_b2": 1, "FA_b3": 1}]
M1 = [{"AJ_b1":0, "AJ_b2": 0, "FA_b1": 1, "FA_b2": 0, "FA_b3": 0}]
M2 = [{"AJ_b1":0, "AJ_b2": 0, "FA_b1": 1, "FA_b2": 1, "FA_b3": 0}]
M3 = [{"AJ_b1":0, "AJ_b2": 0, "FA_b1": 1, "FA_b2": 1, "FA_b3": 1}]
UN = [{"AJ_b1":0, "AJ_b2": 0, "FA_b1": 0, "FA_b2": 0, "FA_b3": 0}]

phenotypes = [E1,H1,H2,H3,M1,M2,M3,UN]

AVOID_H = [{"AJ_b1": 0, "AJ_b2": 0}, {"FA_b1": 0,"FA_b2": 0, "FA_b3": 0}]

if __name__ == "__main__":

    network = "selvaggio_emt"  # "grieco_mapk" # "selvaggio_emt"
    target = AVOID_H    
    
    update = "asynchronous"
    lower_limit = 0
    limit = 2

    primes = get_primes(network)
    nodes = ['AJ_b1', 'AJ_b2', 'AKT', 'BCat', 'BCat_AJ', 'CK1', 'CSL', 'DELTA', 'DVL', 'ECM', 'ECad', 'ECad_AJ_b1', 'ECad_AJ_b2', 'EGF',
             'EGFR', 'ERK', 'FAK_SRC_b1', 'FAK_SRC_b2', 'FAT4', 'FAT4_L', 'FA_b1', 'FA_b2', 'FA_b3', 'GSK3B', 'HGF', 'HGFR', 'HIF1a', 'IL6',
             'ILK', 'ITG_AB', 'JAK', 'JNK', 'LATS', 'MEK', 'NFkB', 'NOTCH', 'PAK', 'PI3K', 'RAF1', 'RAP1', 'RAS', 'ROS', 'RPTP', 'RPTP_L',
             'SLUG', 'SMAD', 'SNAIL', 'STAT3', 'TCF_LEF', 'TGFB', 'TGFBR', 'WNT', 'YAP_TAZ', 'ZEB', 'miR200', 'p120_AJ']
    nodes.remove('BCat')
    nodes.remove('CSL')
    nodes.remove('SMAD')
    nodes.remove('TCF_LEF')
    nodes.remove('miR200')
    
    control_strategies = compute_control_strategies_with_model_checking(
        primes=primes,
        target=target,
        update=update,
        limit=limit,
        starting_length=lower_limit,
        known_strategies=[],
        avoid_nodes=['AJ_b1','AJ_b2','FA_b1','FA_b2','FA_b3','BCat','CSL','SMAD','TCF_LEF','miR200'])
    
    
    
    print("Number of control strategies:", len(control_strategies))
    print("Control strategies:", control_strategies)