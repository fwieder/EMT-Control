
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
   
    
    control_strategies = compute_control_strategies_with_model_checking(
        primes=primes,
        target=target,
        update=update,
        limit=limit,
        starting_length=lower_limit,
        known_strategies=[],
        avoid_nodes=['AJ_b1','AJ_b2','FA_b1','FA_b2','FA_b3'])
    
    
    
    print("Number of control strategies:", len(control_strategies))
    print("Control strategies:", control_strategies)