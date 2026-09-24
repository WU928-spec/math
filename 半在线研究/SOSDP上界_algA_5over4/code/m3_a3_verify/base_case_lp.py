import numpy as np
from scipy.optimize import linprog
from itertools import product
from math import sqrt

c = (1 + sqrt(37)) / 6   # 1.18046042171637...

# ---------------- exact A3 simulator (worst case over least-loaded ties) ------
def simulate_a3_all(p):
    """Return set of possible makespans over all least-loaded tie choices."""
    n = len(p)
    if n == 0:
        return {0.0}
    loads0 = [0.0, 0.0, 0.0]
    for i in range(min(3, n)):
        loads0[i] = p[i]
    if n <= 3:
        return {max(loads0)}
    L0 = max(p[0], p[2] + p[3])
    if n == 4:
        if p[0] + p[3] <= c * L0:
            return {max(p[0] + p[3], p[1], p[2])}
        else:
            return {max(p[0], p[1], p[2] + p[3])}
    # n == 5
    if p[0] + p[3] <= c * L0:
        return {max(p[0] + p[3], p[1] + p[4], p[2])}
    L = max(L0, min(p[1] + p[4], p[2] + p[3] + p[4]))
    loads = [p[0], p[1], p[2] + p[3]]
    if p[0] + p[4] <= c * L:
        return {max(p[0] + p[4], p[1], p[2] + p[3])}
    m = min(loads)
    res = set()
    for idx in range(3):
        if abs(loads[idx] - m) < 1e-15:
            l2 = list(loads)
            l2[idx] += p[4]
            res.add(max(l2))
    return res


def brute_cstar(p):
    n = len(p)
    best = None
    best_assign = None
    for assign in product(range(3), repeat=n):
        loads = [0.0, 0.0, 0.0]
        for i, bb in enumerate(assign):
            loads[bb] += p[i]
        m = max(loads)
        if best is None or m < best - 1e-15:
            best = m
            best_assign = assign
    return best, best_assign


# ---------------- LP machinery -------------------------------------------------
def monotonicity(n):
    cons = []
    for i in range(n - 1):
        v = [0.0] * n
        v[i] = -1.0
        v[i + 1] = 1.0
        cons.append((v, 0.0))          # p_{i+1} - p_i <= 0
    return cons


def run_branch(n, branch_cons, loads, assignment):
    """max over the given branch polytope (intersected with one bin packing)
       of max_machine(load_m . x).  Returns (value, x, load_index)."""
    cons = monotonicity(n)
    for b in range(3):
        v = [0.0] * n
        for i, bb in enumerate(assignment):
            if bb == b:
                v[i] = 1.0
        cons.append((v, 1.0))          # sum of jobs in bin b <= 1
    cons += branch_cons
    A = np.array([cc for cc, _ in cons], dtype=float)
    b = np.array([rhs for _, rhs in cons], dtype=float)
    best = -1e300
    best_x = None
    best_li = -1
    for li, lv in enumerate(loads):
        res = linprog(c=[-x for x in lv], A_ub=A, b_ub=b,
                      bounds=[(0, None)] * n, method="highs")
        if res.status == 2:            # infeasible for this assignment
            continue
        if res.status != 0:
            return None, None, None    # signal anomaly; caller reports
        val = -res.fun
        if val > best + 1e-15:
            best = val
            best_x = res.x
            best_li = li
    return best, best_x, best_li


# ---------------- branch enumeration ------------------------------------------
def build_branches(n):
    if n == 3:
        return [("n3", [], [[1, 0, 0], [0, 1, 0], [0, 0, 1]])]
    if n == 4:
        br = []
        br.append(("n4_L0p1_T",   [([-1, 0, 1, 1], 0.0), ([1 - c, 0, 0, 1], 0.0)],
                   [[1, 0, 0, 1], [0, 1, 0, 0], [0, 0, 1, 0]]))
        br.append(("n4_L0p1_F",   [([-1, 0, 1, 1], 0.0), ([c - 1, 0, 0, -1], 0.0)],
                   [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1]]))
        br.append(("n4_L0p34_T",  [([1, 0, -1, -1], 0.0), ([1, 0, -c, 1 - c], 0.0)],
                   [[1, 0, 0, 1], [0, 1, 0, 0], [0, 0, 1, 0]]))
        br.append(("n4_L0p34_F",  [([1, 0, -1, -1], 0.0), ([-1, 0, c, c - 1], 0.0)],
                   [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 1]]))
        return br
    # n == 5
    br = []
    # step 2 true
    br.append(("n5_L0p1_T",  [([-1, 0, 1, 1, 0], 0.0), ([1 - c, 0, 0, 1, 0], 0.0)],
               [[1, 0, 0, 1, 0], [0, 1, 0, 0, 1], [0, 0, 1, 0, 0]]))
    br.append(("n5_L0p34_T", [([1, 0, -1, -1, 0], 0.0), ([1, 0, -c, 1 - c, 0], 0.0)],
               [[1, 0, 0, 1, 0], [0, 1, 0, 0, 1], [0, 0, 1, 0, 0]]))

    # step 2 false: base + condition + L-case + step3
    e1p5 = [1, 0, 0, 0, 1]
    cases = []
    # L0 = p1
    base1 = ([ -1, 0, 1, 1, 0], 0.0)      # p3+p4 <= p1
    cf1   = ([ c - 1, 0, 0, -1, 0], 0.0)  # p1+p4 >= c p1
    cases.append(("L0p1", base1, cf1, [
        ("Lp1_m1", [([-1, 1, 0, 0, 1], 0.0), ([0, 1, -1, -1, 0], 0.0)], [1, 0, 0, 0, 0]),
        ("Lp1_m2", [([-1, 0, 1, 1, 1], 0.0), ([0, -1, 1, 1, 0], 0.0)], [1, 0, 0, 0, 0]),
        ("Lm1",    [([1, -1, 0, 0, -1], 0.0), ([0, 1, -1, -1, 0], 0.0)], [0, 1, 0, 0, 1]),
        ("Lm2",    [([1, 0, -1, -1, -1], 0.0), ([0, -1, 1, 1, 0], 0.0)], [0, 0, 1, 1, 1]),
    ]))
    # L0 = p3+p4
    base2 = ([1, 0, -1, -1, 0], 0.0)      # p1 <= p3+p4
    cf2   = ([-1, 0, c, c - 1, 0], 0.0)   # p1+p4 >= c(p3+p4)
    cases.append(("L0p34", base2, cf2, [
        ("Lp34_m1", [([0, 1, -1, -1, 1], 0.0), ([0, 1, -1, -1, 0], 0.0)], [0, 0, 1, 1, 0]),
        ("Lp34_m2", [([0, 0, 0, 0, 1], 0.0), ([0, -1, 1, 1, 0], 0.0)], [0, 0, 1, 1, 0]),
        ("Lm1",     [([0, -1, 1, 1, -1], 0.0), ([0, 1, -1, -1, 0], 0.0)], [0, 1, 0, 0, 1]),
        ("Lm2",     [([0, 0, 0, 0, -1], 0.0), ([0, -1, 1, 1, 0], 0.0)], [0, 0, 1, 1, 1]),
    ]))

    loads_true = [[1, 0, 0, 0, 1], [0, 1, 0, 0, 0], [0, 0, 1, 1, 0]]   # p1+p5, p2, p3+p4
    loads_M2   = [[1, 0, 0, 0, 0], [0, 1, 0, 0, 1], [0, 0, 1, 1, 0]]   # p1, p2+p5, p3+p4
    loads_M3   = [[1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 1, 1]]   # p1, p2, p3+p4+p5

    for cname, base, cf, Lcases in cases:
        for lname, lcons, Lvec in Lcases:
            cons = [base, cf] + lcons
            ct = [e1p5[k] - c * Lvec[k] for k in range(5)]   # p1+p5 <= c L
            cf_ = [c * Lvec[k] - e1p5[k] for k in range(5)]  # p1+p5 >= c L
            br.append((f"n5_{cname}_{lname}_S3T", cons + [(ct, 0.0)], loads_true))
            br.append((f"n5_{cname}_{lname}_S3F_M1",
                       cons + [(cf_, 0.0), ([1, -1, 0, 0, 0], 0.0), ([1, 0, -1, -1, 0], 0.0)], loads_true))
            br.append((f"n5_{cname}_{lname}_S3F_M2",
                       cons + [(cf_, 0.0), ([-1, 1, 0, 0, 0], 0.0), ([0, 1, -1, -1, 0], 0.0)], loads_M2))
            br.append((f"n5_{cname}_{lname}_S3F_M3",
                       cons + [(cf_, 0.0), ([-1, 0, 1, 1, 0], 0.0), ([0, -1, 1, 1, 0], 0.0)], loads_M3))
    return br


def main():
    print(f"c = {c:.15f}")
    print("=" * 90)
    for n in (3, 4, 5):
        branches = build_branches(n)
        assignments = list(product(range(3), repeat=n))
        anomalies = []
        per_branch = []
        for name, cons, loads in branches:
            best = -1e300
            bx = None
            bassign = None
            for assign in assignments:
                val, x, li = run_branch(n, cons, loads, assign)
                if val is None:
                    anomalies.append((name, assign))
                    continue
                if val > best + 1e-15:
                    best, bx, bassign = val, x, assign
            per_branch.append((best, bx, bassign, name))
        per_branch.sort(key=lambda t: -t[0])
        R = per_branch[0][0]
        print(f"\n### n = {n} : R_n = {R:.12f}   R_n/c = {R/c:.12f}   {'<= c' if R <= c + 1e-9 else '> c  !!'}")
        print(f"    branches (name : optimal value):")
        for best, _, _, name in per_branch:
            print(f"      {name:28s} {best:.12f}")
        # achieving instance
        best, bx, bassign, name = per_branch[0]
        cstar, cassign = brute_cstar(list(bx))
        loads = None
        # recompute final machine loads for the branch of the winner
        for nm, cons, lds in branches:
            if nm == name:
                loads = [sum(ld[j] * bx[j] for j in range(n)) for ld in lds]
        print(f"    achieving branch: {name}")
        print(f"    x (p1..pn) = {[round(v, 4) for v in bx]}")
        print(f"    A3 final machine loads = {[round(v, 6) for v in loads]}  (makespan={max(loads):.12f})")
        print(f"    brute C* = {cstar:.12f}   ratio(rounded x) = {max(loads)/cstar if cstar>1e-12 else 0:.12f}")
        sim = simulate_a3_all(list(bx))
        print(f"    simulator makespan over ties = {[round(v, 6) for v in sorted(sim)]}")
        # machine grouping for C*
        groups = [[], [], []]
        for i, bb in enumerate(cassign):
            groups[bb].append(round(bx[i], 4))
        print(f"    optimal packing (C*) groups: M1={groups[0]} M2={groups[1]} M3={groups[2]}")
        print(f"    anomalies (non-optimal/error LP statuses): {len(anomalies)}")
    print("\n" + "=" * 90)
    print("done")


if __name__ == "__main__":
    main()
