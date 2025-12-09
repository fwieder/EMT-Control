import logging, math, os, tempfile, shutil, tqdm
from itertools import combinations, product
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Optional
from pyboolnet.prime_implicants import find_inputs, find_constants, percolate, remove_variables
from pyboolnet.trap_spaces import compute_trap_spaces
from pyboolnet.attractors import completeness
from pyboolnet.model_checking import model_checking
from pyboolnet.temporal_logic import subspace2proposition
from pyboolnet.helpers import dicts_are_consistent

log = logging.getLogger(__name__)

# --- Core helpers ------------------------------------------------------------

def is_included_in_subspace(a: dict, b: dict) -> bool:
    """Return True if subspace a contains b."""
    return all(x in a and a[x] == b[x] for x in b)

def EFAG_set_of_subspaces(primes: dict, subs: List[dict]) -> str:
    """Return CTL EF(AG(...)) formula for union of subspaces."""
    return f"EF(AG({' | '.join(subspace2proposition(primes, s) for s in subs)}))"

def fix_components_and_reduce(primes: dict, sub: dict, keep: List[str] = []) -> dict:
    """Fix vars in sub, percolate, and remove constants not in keep."""
    p = percolate(primes, add_constants=sub, copy=True)
    rem = [k for k in find_constants(p) if k not in keep]
    return remove_variables(p, rem, copy=True)

# --- Control strategy tests ---------------------------------------------------

def select_control_strategies_by_percolation(primes, strategies, target):
    """Select strategies that percolate into target."""
    out = []
    for s in strategies:
        perc = find_constants(percolate(primes, add_constants=s, copy=True))
        if any(is_included_in_subspace(perc, t) for t in target): out.append(s)
    return out

def control_direct_percolation(primes, cand, target):
    """Check if cand percolates directly into target."""
    perc = find_constants(percolate(primes, add_constants=cand, copy=True))
    if any(is_included_in_subspace(perc, t) for t in target):
        log.info(f"Intervention (only percolation): {cand}")
        return True
    return False

def run_control_query(primes, target, update):
    """Run CTL model-checking query for target."""
    return model_checking(primes, update, "INIT TRUE", "CTLSPEC " + EFAG_set_of_subspaces(primes, target))

def reduce_and_run_control_query(primes, sub, target, update):
    """Reduce by subspace, then run control query."""
    keep = list({k for s in target for k in s})
    return run_control_query(fix_components_and_reduce(primes, sub, keep), target, update)

def control_is_valid_in_trap_spaces(primes, traps, target, update):
    """Check that trap spaces are compatible with target."""
    if not all(any(dicts_are_consistent(ts, t) for t in target) for ts in traps): return False
    for ts in [x for x in traps if not any(is_included_in_subspace(x, t) for t in target)]:
        if not reduce_and_run_control_query(primes, ts, target, update): return False
    return True

def control_completeness(primes, cand, target, update):
    """Completeness-based control check."""
    if not isinstance(target, dict): return log.error("Target must be dict.")
    perc = find_constants(percolate(primes, add_constants=cand, copy=True))
    new = fix_components_and_reduce(primes, perc, list(target))
    traps = compute_trap_spaces(new, "min")
    if not all(is_included_in_subspace(t, target) for t in traps): return False
    if completeness(new, update):
        log.info(f"Intervention (by completeness): {cand}")
        return True
    return False

def control_model_checking(primes, cand, target, update, max_traps=10_000_000):
    """Model-checking-based control check."""
    if not isinstance(target, list): return log.error("Target must be list.")
    perc = find_constants(percolate(primes, add_constants=cand, copy=True))
    keep = list({k for s in target for k in s})
    new = fix_components_and_reduce(primes, perc, keep)
    traps = compute_trap_spaces(new, "min", max_output=max_traps)
    if not control_is_valid_in_trap_spaces(new, traps, target, update): return False
    if run_control_query(new, target, update):
        log.info(f"Intervention (by CTL formula): {cand}")
        return True
    return False

# --- Supporting utilities -----------------------------------------------------

def find_necessary_interventions(primes, target):
    """Find inputs/constants fixed in all target subspaces."""
    res, cands = {}, find_inputs(primes) + list(find_constants(primes))
    for x in cands:
        if all(x in t for t in target) and len({t[x] for t in target}) == 1:
            res[x] = target[0][x]
    return res

def find_common_variables_in_control_strategies(primes, target):
    """Find constants differing in target and required in all CS."""
    common = find_necessary_interventions(primes, target)
    consts = find_constants(primes)
    right = [x for x in consts if x in common and common[x] == consts[x]]
    return {k: v for k, v in common.items() if k not in right}

def is_control_strategy(primes, cand, target, update, max_output=1_000_000):
    """Check if cand is valid control strategy."""
    if not isinstance(target, list): return log.error("Target must be list.")
    if control_direct_percolation(primes, cand, target): return True
    keep = list({k for s in target for k in s})
    new = fix_components_and_reduce(primes, cand, keep)
    traps = compute_trap_spaces(new, "min", max_output=max_output)
    if not control_is_valid_in_trap_spaces(new, traps, target, update): return False
    return run_control_query(new, target, update)

# --- Completeness-based computation -------------------------------------------

def compute_control_strategies_with_completeness(primes, target, update="asynchronous", limit=3,
                                                 avoid=None, start=0, known=None):
    """Enumerate completeness-based control strategies."""
    if isinstance(target, list): return log.error("Target must be dict.")
    avoid, known = avoid or [], known or []
    common = find_common_variables_in_control_strategies(primes, [target])
    cand_vars = [v for v in primes if v not in common and v not in avoid]
    log.info(f"Common vars: {len(common)} | Candidates: {len(cand_vars)}")
    strategies, perc_true, perc_false = known[:], known[:], []
    for i in range(max(0, start - len(common)), limit + 1 - len(common)):
        for vs in combinations(cand_vars, i):
            for ss in product(*[(0, 1)] * i):
                cand = dict(zip(vs, ss)); cand.update(common)
                if any(is_included_in_subspace(cand, x) for x in strategies): continue
                perc = find_constants(percolate(primes, add_constants=cand, copy=True))
                if perc in perc_true:
                    log.info(f"Intervention: {cand}"); strategies.append(cand)
                elif perc not in perc_false:
                    if control_direct_percolation(primes, cand, [target]) or control_completeness(primes, cand, target, update):
                        perc_true.append(perc); strategies.append(cand)
                    else: perc_false.append(perc)
    return strategies

# --- Model-checking-based computation ----------------------------------------

def compute_control_strategies_with_model_checking(primes, target, update="asynchronous", limit=3,
                                                   avoid=None, max_traps=1_000_000, start=0, known=None):
    """Enumerate model-checking-based control strategies."""
    if not isinstance(target, list): return log.error("Target must be list.")
    avoid, known = avoid or [], known or []
    common = find_common_variables_in_control_strategies(primes, target)
    cand_vars = [v for v in primes if v not in common and v not in avoid]
    log.info(f"Common vars: {len(common)} | Candidates: {len(cand_vars)}")
    strategies, perc_true, perc_false = known[:], known[:], []
    for i in range(max(0, start - len(common)), limit + 1 - len(common)):
        log.info(f"Checking size {i + len(common)}")
        for vs in tqdm.tqdm(combinations(cand_vars, i), total=math.comb(len(cand_vars), i)):
            for ss in product(*[(0, 1)] * i):
                cand = dict(zip(vs, ss)); cand.update(common)
                if any(is_included_in_subspace(cand, x) for x in strategies): continue
                perc = find_constants(percolate(primes, add_constants=cand, copy=True))
                if perc in perc_true:
                    log.info(f"Intervention: {cand}"); strategies.append(cand)
                elif perc not in perc_false:
                    if control_direct_percolation(primes, cand, target) or control_model_checking(primes, cand, target, update):
                        perc_true.append(perc); strategies.append(cand)
                    else: perc_false.append(perc)
    return strategies

# --- Parallel version ---------------------------------------------------------

def _evaluate_candidate(args):
    """
    Worker for parallel control strategy evaluation.
    Each worker uses its own temp dir to avoid NuSMV deadlocks.
    """
    primes, candidate, target, update = args
    import tempfile, shutil, os
    tmpdir = tempfile.mkdtemp(prefix=f"pyboolnet_{os.getpid()}_")
    os.environ["PYBOOLNET_TMPDIR"] = tmpdir
    try:
        perc = find_constants(primes=percolate(primes=primes, add_constants=candidate, copy=True))
        if control_direct_percolation(primes, candidate, target):
            result = (candidate, perc, True)
        elif control_model_checking(primes, candidate, target, update):
            result = (candidate, perc, True)
        else:
            result = (candidate, perc, False)
    except Exception as e:
        result = (candidate, None, f"ERROR: {e}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    return result

def compute_control_strategies_with_model_checking_parallel(primes, target, update="asynchronous",
                                                            limit=3, avoid=None, max_traps=1_000_000,
                                                            start=0, known=None, n_jobs=None):
    """Parallel model-checking-based strategy computation."""
    avoid, known = avoid or [], known or []
    strategies, perc_true, perc_false = known[:], known[:], []
    n_jobs = n_jobs or (os.cpu_count() or 1)
    tmpdir = tempfile.mkdtemp(prefix="pyboolnet_")
    log.info(f"Created temp dir: {tmpdir}")
    common = find_common_variables_in_control_strategies(primes, target)
    cand_vars = [v for v in primes if v not in common and v not in avoid]
    log.info(f"Common vars: {len(common)} | Candidates: {len(cand_vars)}")

    for i in range(max(0, start - len(common)), limit + 1 - len(common)):
        tasks = [(primes, {**dict(zip(vs, ss)), **common}, target, update)
                 for vs in combinations(cand_vars, i) for ss in product(*[(0, 1)] * i)
                 if not any(is_included_in_subspace({**dict(zip(vs, ss)), **common}, x) for x in strategies)]

        with ProcessPoolExecutor(max_workers=n_jobs) as exe:
            for fut in tqdm.tqdm(as_completed([exe.submit(_evaluate_candidate, t) for t in tasks]), total=len(tasks), desc=f"size={i}"):
                cand, perc, status = fut.result()
                if isinstance(status, str) and status.startswith("ERROR"):
                    log.warning(f"Error {cand}: {status}"); continue
                if perc in perc_true: strategies.append(cand)
                elif perc not in perc_false:
                    (perc_true if status else perc_false).append(perc)
                    if status: strategies.append(cand)

    try: shutil.rmtree(tmpdir); log.info(f"Deleted temp dir: {tmpdir}")
    except Exception as e: log.warning(f"Could not delete {tmpdir}: {e}")
    return strategies
