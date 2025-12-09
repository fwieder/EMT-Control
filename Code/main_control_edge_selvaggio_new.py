from os import system
from pprint import pformat
from time import time

from control_strategies_trap_spaces import *
from control_strategies_parallel import find_common_variables_in_control_strategies,control_direct_percolation,control_model_checking

from pyboolnet.trap_spaces import compute_trap_spaces, compute_trapspaces_that_intersect_subspace
from pyboolnet.file_exchange import bnet2primes
from pyboolnet.prime_implicants import find_inputs, create_constants, update_primes
from pyboolnet.repository import get_primes


def list_edges_from_primes(primes: dict, avoid_sources: list = [], avoid_targets: list = []):
    """
    Returns a list with all the pairs of nodes (i,j) such that i appears in a prime implicant of j for every i,j in *primes*.
    This implies that there is an edge (i,j) in the interaction graph.
    Pairs (i,j) where i is in *avoid_sources* or j is in *avoid_targets* are not considered.
    
    """
    nodes = [x for x in primes.keys() if x not in avoid_targets]
    edges = set()
    for x in nodes:
        for k in [0,1]:
            for p in primes[x][k]:
                for y in p.keys():
                    if y not in avoid_sources:
                        edges.add((y,x))
    return edges


def fix_edges_and_reduce(primes: dict, interv: dict, keep_vars: list = []):
    
    new_primes = primes

    for e in interv.keys():
        new_primes = update_primes(primes=new_primes, name=e[1], constants={e[0]: interv[e]}, copy=True)
    
    return new_primes


def compute_control_strategies_with_model_checking_node_and_edge(primes: dict, target: List[dict], method: str, intervention_type: str = "node", update: str = "asynchronous", limit: int = 3, avoid_nodes: List[str] = None, avoid_edges: List[tuple] = None, silent: bool = False, max_output_trapspaces: int = 1000000, starting_length: int = 0, previous_cs: List[dict] = None, known_cs: List[dict] = None):

    """
    Identifies control strategies for the *target* subset using model checking.

    **arguments**:
        * *primes*: prime implicants
        * *target*: list of subspaces defining the target subset. When the method is *"completeness"* the list should contain exactly one subspace.
        * *method*: the type of method, either *"completeness"* or *"model_checking"*.
        * *intervention_type*: the type of intervention, either *"node"*, *"edge"* or *"both"*.
        * *update*: the type of update, either *"synchronous"*, *"asynchronous"* or *"mixed"*
        * *limit*: maximal size of the control strategies. Default value: 3.
        * *silent*: if True, does not print infos to screen. Default value: False.
        * *starting_length*: minimum possible size of the control strategies. Default value: 0.
        * *previous_cs*: list of already identified control strategies. Default value: empty list.
        * *avoid_nodes*: list of nodes that cannot be part of the control strategies. Default value: empty list.

    **returns**:
        * *cs_total*: list of control strategies (dict) of *subspace* obtained using completeness.

    **example**::
        >>> ultimate_control_multispace(primes, {'v1': 1}, "asynchronous")

    """

    # Intializing

    if previous_cs is None:
        previous_cs = []
    if avoid_nodes is None:
        avoid_nodes = []
    if avoid_edges is None:
        avoid_edges = []
    if known_cs is None:
        known_cs = []

    # Preliminary setting

    cs_total = previous_cs
    perc_true = known_cs
    perc_false = []
    if type(target) != list:
        print("The target must be a list.")

    common_vars_in_cs = find_common_variables_in_control_strategies(primes, target)
    candidate_variables = [x for x in primes.keys() if x not in common_vars_in_cs.keys() and x not in avoid_nodes]
    candidate_edges = [x for x in list_edges_from_primes(primes, avoid_targets=common_vars_in_cs) if x not in avoid_edges]

    candidates = candidate_variables
  
    if intervention_type == "edge":
        candidates = candidate_edges
    if intervention_type == "both" or intervention_type == "combined":
        candidate_edges = [x for x in candidate_edges if x[0] != x[1]]
        candidates = candidate_variables + candidate_edges

    if not silent:
        print("Number of common variables in the CS:", len(common_vars_in_cs))
        print("Number of candiadate variables:", len(candidates))


    # Computing control strategies

    for i in range(max(0, starting_length - len(common_vars_in_cs)), limit + 1 - len(common_vars_in_cs)):

        if not silent:
            print("Checking control strategies of size", i + len(common_vars_in_cs))

        for vs in combinations(candidates, i):
            subsets = product(*[(0, 1)]*i)

            for ss in subsets:

                # Avoid that node intervention and edge intervention target the same node
                if not any(len(y) == 2 and x == y[1] for x in vs for y in vs):

                    candidate = dict(zip(vs, ss))
                    if intervention_type == "edge":
                        candidate.update(dict(((k,k), common_vars_in_cs[k]) for k in common_vars_in_cs.keys()))
                    else:
                        candidate.update(common_vars_in_cs)

                    if not any(is_included_in_subspace(candidate, x) for x in cs_total):

                        node_intv = dict((x, candidate[x]) for x in candidate.keys() if x in candidate_variables)
                        edge_intv = dict((x, candidate[x]) for x in candidate.keys() if x in candidate_edges)
                            
                        new_primes = fix_edges_and_reduce(primes=primes, interv=edge_intv, keep_vars=primes.keys())  
    
                        if control_direct_percolation(new_primes, node_intv, target):
                            cs_total.append(candidate)

                        else:

                            if method == "completeness":

                                if control_completeness(new_primes, node_intv, target[0], update):
                                    cs_total.append(candidate)
                            else:

                                if control_model_checking(new_primes, node_intv, target, update):
                                    cs_total.append(candidate)

    return cs_total



if __name__ == "__main__":


    control_problem = "avoid_hybrid"


    network = "selvaggio_emt"
    primes = get_primes(network)
    update = "asynchronous"

    name_phenotype = ["E1", "H1", "H2", "H3", "M1", "M2", "M3", "UN"]
    phenotypes = [
        {"AJ_b1":1, "AJ_b2":1, "FA_b1":0, "FA_b2":0, "FA_b3":0}, #E1
        {"AJ_b1":1, "AJ_b2":1, "FA_b1":1, "FA_b2":0, "FA_b3":0}, #H1
        {"AJ_b1":1, "AJ_b2":0, "FA_b1":1, "FA_b2":1, "FA_b3":0}, #H2
        {"AJ_b1":1, "AJ_b2":1, "FA_b1":1, "FA_b2":1, "FA_b3":1}, #H3
        {"AJ_b1":0, "AJ_b2":0, "FA_b1":1, "FA_b2":0, "FA_b3":0}, #M1
        {"AJ_b1":0, "AJ_b2":0, "FA_b1":1, "FA_b2":1, "FA_b3":0}, #M2
        {"AJ_b1":0, "AJ_b2":0, "FA_b1":1, "FA_b2":1, "FA_b3":1}, #M3
        {"AJ_b1":0, "AJ_b2":0, "FA_b1":0, "FA_b2":0, "FA_b3":0}] #UN

    cs_total = []
    
    print("Avoid hybrid")
    limit = 2
    avoid_pheno_nodes = True
    intervention_type = "combined" #options: node, edge, combined
    output_file = "Results/" + network + "_lim" + str(limit) + "_" + intervention_type + "_model_checking_avoid_hybrid"
    target = [
        {'AJ_b1': 0, 'AJ_b2': 0, 'FA_b1': 0, 'FA_b2': 0, 'FA_b3': 0},
        {'AJ_b1': 0, 'AJ_b2': 0, 'FA_b1': 0, 'FA_b2': 0, 'FA_b3': 1},
        {'AJ_b1': 0, 'AJ_b2': 0, 'FA_b1': 0, 'FA_b2': 1, 'FA_b3': 0},
        {'AJ_b1': 0, 'AJ_b2': 0, 'FA_b1': 0, 'FA_b2': 1, 'FA_b3': 1},
        {'AJ_b1': 0, 'AJ_b2': 0, 'FA_b1': 1, 'FA_b2': 0, 'FA_b3': 0},
        {'AJ_b1': 0, 'AJ_b2': 0, 'FA_b1': 1, 'FA_b2': 0, 'FA_b3': 1},
        {'AJ_b1': 0, 'AJ_b2': 0, 'FA_b1': 1, 'FA_b2': 1, 'FA_b3': 0},
        {'AJ_b1': 0, 'AJ_b2': 0, 'FA_b1': 1, 'FA_b2': 1, 'FA_b3': 1},
        {'AJ_b1': 0, 'AJ_b2': 1, 'FA_b1': 0, 'FA_b2': 0, 'FA_b3': 0},
        {'AJ_b1': 1, 'AJ_b2': 0, 'FA_b1': 0, 'FA_b2': 0, 'FA_b3': 0},
        {'AJ_b1': 1, 'AJ_b2': 1, 'FA_b1': 0, 'FA_b2': 0, 'FA_b3': 0}]


    avoid_nodes = []
    avoid_edges = []

    if avoid_pheno_nodes:
        avoid_nodes = target[0].keys()
        avoid_edges = [x for x in list_edges_from_primes(primes) if x not in list_edges_from_primes(primes, avoid_targets=avoid_nodes, avoid_sources=avoid_nodes)]


    cs = compute_control_strategies_with_model_checking_node_and_edge(
        primes=primes,
        target=target,
        method="model_checking",
        intervention_type=intervention_type,
        update=update,
        limit=limit,
        silent=False,
        previous_cs=[],
        known_cs=[],
        avoid_nodes=avoid_nodes,
        avoid_edges=avoid_edges)


    with open(output_file+".py", "w") as f:
        f.write("targets = " + pformat(target) + "\n")
        f.write("#Control strategies" + "\ncs = " + pformat(cs) + "\n")


