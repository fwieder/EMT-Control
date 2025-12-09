#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  5 15:09:24 2025

@author: frederik
"""
import os
from control_strategies_parallel import compute_control_strategies_with_model_checking_parallel
from pyboolnet.repository import get_primes
import json
import pickle
from pathlib import Path

output_dir = Path("control_results")
output_dir.mkdir(exist_ok=True)

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

    control_strategies = compute_control_strategies_with_model_checking_parallel(
        primes=primes,
        target=target,
        update=update,
        limit=limit,
        start=lower_limit,
        known=[],
        avoid=['AJ_b1','AJ_b2','FA_b1','FA_b2','FA_b3'],
        n_jobs=os.cpu_count() - 2
    )

    cs1 = [cs for cs in control_strategies if len(cs) == 1]
    cs2 = [cs for cs in control_strategies if len(cs) == 2]
    #cs3 = [cs for cs in control_strategies if len(cs) == 3]
    #cs4 = [cs for cs in control_strategies if len(cs) == 4]
    
    print("Number of size 1 control strategies:", len(cs1))
    print("Number of size 2 control strategies:", len(cs2))
    #print("Number of size 3 control strategies:", len(cs3))
    #print("Number of size 4 control strategies:", len(cs4))
    
    
    
    """
    # Save intermediate results as JSON
    filename = output_dir / f"{network}_phenotype_6.json"
    with open(filename, "w") as f:
        json.dump({"cs2": cs2, "cs3": cs3}, f, indent=2)

    # Optionally also pickle (faster to reload)
    filename_pickle = output_dir / f"{network}_phenotype_6.pkl"
    with open(filename_pickle, "wb") as f:
        pickle.dump({"cs2": cs2, "cs3": cs3, "cs4": cs4}, f)
    """
"""
import json

filename = "control_results/selvaggio_emt_phenotype_0.json"

with open(filename, "r") as f:
    data = json.load(f)

cs2 = data["cs2"]
cs3 = data["cs3"]

print("Loaded cs2:", cs2)
print("Number of cs2 strategies:", len(cs2))
"""