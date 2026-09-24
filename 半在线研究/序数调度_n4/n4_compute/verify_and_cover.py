"""verify_and_cover.py - for a given profile c and threshold t:
  1. for EVERY structural partition P: find a certified kill witness at t
     (MILP feas solution, numerically verified) or report P survives below t.
  2. greedy set cover: minimal family of value vectors covering all partitions.
Outputs JSON with per-partition witnesses and the minimal script family.
"""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compute import (KillMILP, gen_partitions, partitions_array, opt_value,
                     machine_str, partition_str, distinct_machines,
                     make_library, eval_vectors)


def verify_witness(P, M, r, t, P_arr, n, k):
    """Numerically verify a feas-mode solution kills P at threshold t."""
    v = r["v"]
    asg = r["assign"]
    if v is None or asg is None:
        return False, "no solution"
    if not all(v[i] >= v[i + 1] - 1e-7 for i in range(k - 1)):
        return False, "v not decreasing"
    if v.min() < -1e-9:
        return False, "negative v"
    if abs(sum(M[rr] * v[rr] for rr in range(k)) - 1) > 1e-6:
        return False, "normalization"
    loads = np.zeros(n)
    for j in range(sum(P_arr[0, 0]) if False else len(asg)):
        loads[asg[j]] += v[j if len(np.atleast_1d(v)) > k else j]
    # recompute loads properly: v is per-rank; job j has rank ranks[j]
    return True, loads


def main():
    c = tuple(int(x) for x in sys.argv[1].split(","))
    n = int(sys.argv[2])
    t = float(sys.argv[3])
    outfile = sys.argv[4]
    k = len(c)
    m = sum(c)
    kill = KillMILP(c, n)
    parts = gen_partitions(c, n)
    P_arr = partitions_array(parts, n, k)
    ranks = kill.ranks
    t0 = time.time()

    witness_of = {}      # partition index -> witness dict
    survivors = []
    vectors = []         # pool of witness vectors (numpy)
    vec_index = {}       # partition index -> vector id that kills it

    # pre-kill with library vectors to cut MILP calls
    lib = make_library(k, n)
    LB = eval_vectors(P_arr, lib)
    lib_vec_ids = []
    for v in lib:
        vectors.append(np.asarray(v, float))
    for i in range(len(parts)):
        if LB[i] >= t - 1e-9:
            witness_of[i] = {"via": "library"}
    todo = [i for i in range(len(parts)) if i not in witness_of]
    print(f"{len(parts)} partitions, {len(todo)} need MILP kill test", flush=True)

    for cnt, i in enumerate(todo):
        P = parts[i]
        found = None
        for M in distinct_machines(P):
            r = kill.solve(M, mode="feas", t=t)
            if r["ok"]:
                found = (M, r)
                break
        if found is None:
            survivors.append(i)
            continue
        M, r = found
        v = r["v"]
        # numeric verification
        ok = (all(v[a] >= v[a + 1] - 1e-7 for a in range(k - 1))
              and v.min() >= -1e-9
              and abs(sum(M[a] * v[a] for a in range(k)) - 1) < 1e-6)
        loads = np.zeros(n)
        for j in range(m):
            loads[r["assign"][j]] += v[ranks[j]]
        ok = ok and loads.max() <= 1.0 / t + 1e-7
        # direct ratio check with exact OPT
        Mrow = np.array([list(mm) for mm in P])
        CP = float((Mrow @ v).max())
        OPT = opt_value(P_arr, v)
        ratio = CP / OPT
        ok = ok and ratio >= t - 1e-6
        if not ok:
            survivors.append(i)
            witness_of[i] = {"via": "FAILED_VERIFICATION"}
            print(f"WARNING verification failed for partition {i}", flush=True)
            continue
        witness_of[i] = {
            "via": "milp", "machine": machine_str(M),
            "v": [round(float(x), 8) for x in v],
            "packing_loads": [round(float(x), 6) for x in loads],
            "ratio_at_v": round(ratio, 6),
        }
        vectors.append(v.copy())
        vec_index[i] = len(vectors) - 1
        if cnt % 500 == 0:
            print(f"  {cnt}/{len(todo)} killed, {len(survivors)} survivors "
                  f"[{time.time()-t0:.0f}s]", flush=True)

    # ---- greedy set cover over witness vectors ----
    # coverage: vector v covers partition i if C_P(v)/OPT(v) >= t - 1e-9
    # chunked to bound memory: (np, n, nv) intermediates
    Vmat = np.array(vectors)                     # (nv, k)
    nv = len(vectors)
    nP = len(parts)
    Pf = P_arr.astype(np.float32)
    # pass 1: exact OPT per vector (min over ALL partitions)
    opt_all = np.full(nv, np.inf)
    CH = 2000
    for i0 in range(0, nP, CH):
        sl = slice(i0, min(i0 + CH, nP))
        loads = np.einsum("pnk,vk->pnv", Pf[sl], Vmat)
        np.minimum(opt_all, loads.max(axis=1).min(axis=0), out=opt_all)
        del loads
    # pass 2: coverage with the global OPT
    cover = np.zeros((nP, nv), dtype=bool)
    for i0 in range(0, nP, CH):
        sl = slice(i0, min(i0 + CH, nP))
        loads = np.einsum("pnk,vk->pnv", Pf[sl], Vmat)
        cmax = loads.max(axis=1)
        cover[sl] = (cmax / opt_all[None, :]) >= t - 1e-9
        del loads, cmax

    # verify full coverage
    covered_any = cover.any(axis=1)
    uncovered = [i for i in range(len(parts)) if not covered_any[i]]
    print(f"pool covers {covered_any.sum()}/{len(parts)} partitions at t={t}",
          flush=True)

    uncovered_set = set(range(len(parts)))
    family = []
    cover_list = [set(np.where(cover[:, j])[0]) for j in range(len(vectors))]
    while uncovered_set:
        best_j, best_gain = -1, -1
        for j, S in enumerate(cover_list):
            g = len(S & uncovered_set)
            if g > best_gain:
                best_gain, best_j = g, j
        if best_gain <= 0:
            break
        family.append(best_j)
        uncovered_set -= cover_list[best_j]
    print(f"greedy family size: {len(family)}", flush=True)

    out = {
        "profile": list(c), "n": n, "threshold": t,
        "num_partitions": len(parts),
        "num_survivors_below_t": len(survivors),
        "survivors": [partition_str(parts[i]) for i in survivors[:50]],
        "survivor_idx": survivors,
        "family": [
            {"v": [round(float(x), 8) for x in vectors[j]],
             "covers": len(cover_list[j])} for j in family],
        "family_covers_union": len(parts) - len(uncovered_set),
        "time": round(time.time() - t0, 1),
    }
    with open(outfile, "w") as f:
        json.dump(out, f)
    print("written", outfile, flush=True)


if __name__ == "__main__":
    main()
