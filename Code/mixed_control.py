#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 14:47:00 2025

@author: frederik
"""


from pyboolnet.repository import get_primes
from control_strategies_trap_spaces import run_control_problem, results_info
from itertools import product

if __name__ == "__main__":
   network = "selvaggio_emt"
   primes = get_primes(network)
   targets = {
           "E1": {"AJ_b1": 1, "AJ_b2": 1, "FA_b1": 0, "FA_b2": 0, "FA_b3": 0},
           "H1": {"AJ_b1": 1, "AJ_b2": 1, "FA_b1": 1, "FA_b2": 0, "FA_b3": 0},
           "H2": {"AJ_b1": 1, "AJ_b2": 0, "FA_b1": 1, "FA_b2": 1, "FA_b3": 0},
           "H3": {"AJ_b1": 1, "AJ_b2": 1, "FA_b1": 1, "FA_b2": 1, "FA_b3": 1},
           "M1": {"AJ_b1": 0, "AJ_b2": 0, "FA_b1": 1, "FA_b2": 0, "FA_b3": 0},
           "M2": {"AJ_b1": 0, "AJ_b2": 0, "FA_b1": 1, "FA_b2": 1, "FA_b3": 0},
           "M3": {"AJ_b1": 0, "AJ_b2": 0, "FA_b1": 1, "FA_b2": 1, "FA_b3": 1},
           "UN": {"AJ_b1": 0, "AJ_b2": 0, "FA_b1": 0, "FA_b2": 0, "FA_b3": 0},
   }
   
   input_edges = [("ROS","JNK"),("ROS","NFkB"),("ROS","RPTP"),("ROS","FAK_SRC"),
                  ("IL6","JAK"),("DELTA","NOTCH"),("TGFB","TGFBR"),("FAT4_L","FAT4"),
                  ("EGF","EGFR"),("ECM","ITG_AB"),("HGF","HGFR"),("RPTP_L","RPTP"),("WNT","C4K1")]
   
   variables = list(primes)   
   for phenotype in targets:

       intervention_type = "combined"  # Options: "node", "edge", "combined"
       control_type = "percolation"  # Options: "percolation","trap_spaces", "both"
       update = "asynchronous"
       target = targets[phenotype]
       print("TARGET", targets[phenotype])
       avoid_nodes = list(target)
       avoid_edges = [e for e in product(variables, variables) if (e[0] == e[1]) or (e[0] in avoid_nodes) or (e[1] in avoid_nodes)]
       limit = 3
       use_attractors = True
       complex_attractors = []
       output_file = f"control_results/traps-spaces-{phenotype}-{intervention_type}-{control_type}"

       print(f"Phenotype: {phenotype}, Type: {intervention_type} -{control_type}")

       cs = run_control_problem(
           primes=primes,
           target=target,
           intervention_type=intervention_type,
           control_type=control_type,
           avoid_nodes=avoid_nodes,
           avoid_edges=avoid_edges,
           limit=limit,
           output_file=output_file,
           use_attractors=use_attractors,
           complex_attractors=complex_attractors)

       print(results_info(cs))
       
       cs2 = [strat for strat in cs if len(strat) == 2]
       print(cs2)