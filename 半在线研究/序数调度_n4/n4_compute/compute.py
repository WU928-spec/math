"""
compute.py - exact min-max computation for offline ordinal scheduling
(Liu-Sidney-van Vliet 1996 model; adversarial lower bound framework).

Model: n identical machines, adversary publishes rank profile c=(c_1..c_k),
m=sum c_i jobs (c_r jobs of rank r). Algorithm picks a structural partition P
of the m jobs into n (unlabeled, possibly empty) machines. Adversary then picks
strictly decreasing v_1>...>v_k>0. ratio(P,v)=C_P(v)/OPT(v).

Key identity (exact, no bisection needed):
  sup_{v strictly decreasing} load(M*,v)/OPT(v)
    = 1 / min{ s : exists weakly decreasing v with load(M*,v)=1 and a packing
                 of all jobs into n bins of load <= s }
(sup over strict = sup over weak by continuity/density; normalization by
scale invariance). The RHS is one MILP per machine M* of P (min-s MILP).
Attained vs only-approached is checked by a max-eps MILP at the boundary.

Machines are multisets of ranks (count vectors); partitions are multisets of
machines (structural enumeration, same-rank symmetry removed).
"""
import numpy as np
from itertools import product
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import coo_array

EPS_STRICT = 1e-6   # epsilon above this => strict witness exists


# ---------------------------------------------------------------------------
# structural partition enumeration
# ---------------------------------------------------------------------------

def gen_machines(c):
    """All nonzero count vectors d with 0<=d_i<=c_i, sorted desc (canonical)."""
    c = tuple(c)
    ms = [d for d in product(*[range(ci + 1) for ci in c]) if any(d)]
    ms.sort(reverse=True)
    return ms


def gen_partitions(c, n):
    """All multisets of <= n machines whose count vectors sum exactly to c."""
    c = tuple(c)
    k = len(c)
    machines = gen_machines(c)
    parts = []

    def rec(rem, start, used, cur):
        if not any(rem):
            parts.append(tuple(cur))
            return
        if used == n:
            return
        for i in range(start, len(machines)):
            mm = machines[i]
            ok = True
            for j in range(k):
                if mm[j] > rem[j]:
                    ok = False
                    break
            if ok:
                cur.append(mm)
                rec(tuple(rem[j] - mm[j] for j in range(k)), i, used + 1, cur)
                cur.pop()

    rec(c, 0, 0, [])
    return parts


def partitions_array(parts, n, k):
    P = np.zeros((len(parts), n, k), dtype=np.int32)
    for i, p in enumerate(parts):
        for j, mm in enumerate(p):
            P[i, j, :] = mm
    return P


def machine_str(mm):
    """count vector -> readable multiset of 1-indexed ranks, e.g. {1,1,3}."""
    s = []
    for r, d in enumerate(mm):
        s += [str(r + 1)] * d
    return "{" + ",".join(s) + "}"


def partition_str(p):
    return " | ".join(machine_str(mm) for mm in p)


# ---------------------------------------------------------------------------
# heuristic value-vector library
# ---------------------------------------------------------------------------

def make_library(k, n, seed=0):
    V = []
    V.append([2 * n - r for r in range(1, k + 1)])                 # Graham-like
    V.append([max(2 * n - r, 1.0) for r in range(1, k + 1)])       # truncated Graham
    V.append([k + 1 - r for r in range(1, k + 1)])                 # linear
    V.append([2 * (k + 1 - r) for r in range(1, k + 1)])
    V.append([(k + 1 - r) ** 2 for r in range(1, k + 1)])          # convex
    V.append([(k + 1 - r) ** 3 for r in range(1, k + 1)])
    V.append([(k + 1 - r) ** 4 for r in range(1, k + 1)])
    V.append([float(max(k + 1 - r, 1)) for r in range(1, k + 1)])
    # two-level: top a ranks = H, rest = 1
    for a in range(1, k):
        for H in [1.2, 1.5, 2.0, 3.0, 5.0, 10.0, 50.0]:
            V.append([H] * a + [1.0] * (k - a))
    # three-level
    for a in range(1, k):
        for b in range(a + 1, k):
            for H1, H2 in [(3, 2), (5, 2), (2, 1.5), (4, 1.5), (10, 3), (3, 1.5)]:
                V.append([H1] * a + [H2] * (b - a) + [1.0] * (k - b))
    # geometric decay
    for q in [1.05, 1.1, 1.2, 1.35, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0]:
        V.append([q ** (k - r) for r in range(1, k + 1)])
    V.append([1.0 / r for r in range(1, k + 1)])
    V.append([1.0 / r ** 2 for r in range(1, k + 1)])
    # staircase with pairs/triples (7,7,6,6,5,5,... / 7,7,7,6,6,6,...)
    V.append([float((k + 1 - r + 1) // 2) for r in range(1, k + 1)])
    V.append([float((k + 1 - r + 2) // 3) for r in range(1, k + 1)])
    # skew: v1 huge, v1=v2 huge
    V.append([100.0] + [1.0] * (k - 1))
    if k >= 2:
        V.append([100.0, 99.0] + [1.0] * (k - 2))
    # random decreasing
    rng = np.random.default_rng(seed)
    for _ in range(40):
        xs = np.sort(rng.random(k) * 3 + 0.05)[::-1]
        V.append(list(xs))
        xs = (np.cumsum(rng.exponential(1.0, k)) + 0.1)[::-1]
        V.append(list(xs))
    out = []
    for v in V:
        v = np.asarray(v, float)
        # validity: weakly decreasing, nonnegative, v_1 > 0
        # (negative entries would invalidate OPT-based ratios)
        if np.all(np.diff(v) <= 0) and v.min() >= 0.0 and v[0] > 0:
            out.append(v)
    return out


def eval_vectors(P_arr, vectors):
    """LB[p] = max over vectors of C_P(v)/OPT(v). OPT over all partitions."""
    LB = np.zeros(len(P_arr))
    for v in vectors:
        v = np.asarray(v, float)
        assert v.min() >= 0.0 and v[0] > 0, f"invalid library vector {v}"
        loads = P_arr @ v
        cmax = loads.max(axis=1)
        opt = cmax.min()
        ratio = cmax / opt
        np.maximum(LB, ratio, out=LB)
    return LB


def opt_value(P_arr, v):
    loads = P_arr @ np.asarray(v, float)
    return loads.max(axis=1).min()


# ---------------------------------------------------------------------------
# MILP: min over (weakly decreasing v, load(M*)=1, packing) of max bin load s
# ---------------------------------------------------------------------------

class KillMILP:
    """Variables: x[j,b] (bin), w[j,b]=v_rank(j)*x[j,b] linearized, v[r], s, eps.

    Modes:
      min_s     : minimize s                      -> exact sup ratio = 1/s*
      feas      : s <= 1/t fixed, objective 0     -> kill test at threshold t
      max_eps   : s <= 1/t fixed, maximize eps    -> strict-attainability check
    """

    def __init__(self, c, n):
        self.c = tuple(c)
        self.n = n
        self.k = len(c)
        self.m = sum(c)
        self.ranks = []
        for r in range(self.k):
            self.ranks += [r] * self.c[r]
        m, k, n_ = self.m, self.k, self.n
        self.N = 2 * m * n_ + k + 2

    def xid(self, j, b):
        return j * self.n + b

    def wid(self, j, b):
        return self.m * self.n + j * self.n + b

    def vid(self, r):
        return 2 * self.m * self.n + r

    @property
    def sid(self):
        return 2 * self.m * self.n + self.k

    @property
    def eid(self):
        return 2 * self.m * self.n + self.k + 1

    def _build(self, M_star):
        """Static part: rows independent of mode. Returns list of
        (entries, lo, hi) plus handles for mode-dependent bounds."""
        m, k, n = self.m, self.k, self.n
        M = float(m)                      # big-M upper bound on v_r (<= s <= m)
        rows = []

        def add(entries, lo, hi):
            rows.append((entries, lo, hi))

        for j in range(m):                                   # assignment
            add([(self.xid(j, b), 1.0) for b in range(n)], 1.0, 1.0)
        for b in range(n):                                   # bin capacity <= s
            add([(self.wid(j, b), 1.0) for j in range(m)] + [(self.sid, -1.0)],
                -np.inf, 0.0)
        for j in range(m):                                   # w <= v_r
            r = self.ranks[j]
            for b in range(n):
                add([(self.wid(j, b), 1.0), (self.vid(r), -1.0)], -np.inf, 0.0)
        for j in range(m):                                   # w <= M*x
            for b in range(n):
                add([(self.wid(j, b), 1.0), (self.xid(j, b), -M)], -np.inf, 0.0)
        for j in range(m):                                   # w >= v_r - M(1-x)
            r = self.ranks[j]
            for b in range(n):
                add([(self.wid(j, b), -1.0), (self.vid(r), 1.0),
                     (self.xid(j, b), M)], -np.inf, M)
        for r in range(k):                                   # v_r <= s
            add([(self.vid(r), 1.0), (self.sid, -1.0)], -np.inf, 0.0)
        add([(self.vid(r), float(M_star[r])) for r in range(k) if M_star[r]],
            1.0, 1.0)                                        # load(M*) = 1
        for r in range(k - 1):                               # v_r - v_{r+1} >= eps
            add([(self.vid(r), -1.0), (self.vid(r + 1), 1.0), (self.eid, 1.0)],
                -np.inf, 0.0)
        add([(self.vid(k - 1), -1.0), (self.eid, 1.0)], -np.inf, 0.0)
        # total load <= n*s
        add([(self.vid(r), float(self.c[r])) for r in range(k)] + [(self.sid, -float(n))],
            -np.inf, 0.0)
        # symmetry break: bin index non-decreasing among same-rank jobs
        for j in range(m - 1):
            if self.ranks[j] == self.ranks[j + 1]:
                ents = [(self.xid(j + 1, b), float(b)) for b in range(n)]
                ents += [(self.xid(j, b), -float(b)) for b in range(n)]
                add(ents, 0.0, np.inf)
        return rows

    def solve(self, M_star, mode="min_s", t=None):
        m, k, n = self.m, self.k, self.n
        rows = self._build(M_star)
        rr, cc, dd, lb, ub = [], [], [], [], []
        for i, (ents, lo, hi) in enumerate(rows):
            for col, val in ents:
                rr.append(i)
                cc.append(col)
                dd.append(val)
            lb.append(lo)
            ub.append(hi)
        A = coo_array((dd, (rr, cc)), shape=(len(rows), self.N)).tocsr()
        con = LinearConstraint(A, np.array(lb), np.array(ub))

        obj = np.zeros(self.N)
        lbnd = np.zeros(self.N)
        ubnd = np.full(self.N, np.inf)
        for j in range(m):
            for b in range(n):
                ubnd[self.xid(j, b)] = 1.0
                ubnd[self.wid(j, b)] = float(m)
        for r in range(k):
            ubnd[self.vid(r)] = float(m)
        ubnd[self.sid] = float(m)
        if mode == "min_s":
            obj[self.sid] = 1.0
            ubnd[self.eid] = 0.0                    # eps = 0 (weakly decreasing)
        elif mode == "feas":
            ubnd[self.sid] = 1.0 / t
            ubnd[self.eid] = 0.0
        elif mode == "max_eps":
            ubnd[self.sid] = 1.0 / t
            obj[self.eid] = -1.0
            ubnd[self.eid] = 1.0
        else:
            raise ValueError(mode)
        integrality = np.zeros(self.N)
        for j in range(m):
            for b in range(n):
                integrality[self.xid(j, b)] = 1.0
        res = milp(obj, integrality=integrality, bounds=Bounds(lbnd, ubnd),
                   constraints=con,
                   options={"time_limit": 300, "disp": False,
                            "mip_rel_gap": 0.0})
        out = {"ok": False, "s": None, "eps": None, "v": None, "assign": None,
               "status": res.status}
        if res.status == 0 and res.x is not None:
            out["ok"] = True
            out["s"] = float(res.x[self.sid])
            out["eps"] = float(res.x[self.eid])
            out["v"] = np.array([res.x[self.vid(r)] for r in range(k)])
            xa = np.array([[res.x[self.xid(j, b)] for b in range(n)]
                           for j in range(m)])
            out["assign"] = xa.argmax(axis=1)
        return out

    # convenience wrappers -------------------------------------------------
    def sup_ratio(self, M_star):
        """Exact sup_v load(M*,v)/OPT(v) = 1/s* (weak-closure value)."""
        r = self.solve(M_star, mode="min_s")
        if not r["ok"]:
            raise RuntimeError(f"min_s MILP failed, status {r['status']}")
        r["ratio"] = 1.0 / r["s"]
        return r

    def killed_at(self, M_star, t):
        """True if sup ratio(M*) >= t (weak sense: approached counts)."""
        return self.solve(M_star, mode="feas", t=t)["ok"]

    def strict_attained(self, M_star, t):
        """(attained?, eps, witness) : strictly decreasing v with ratio >= t."""
        r = self.solve(M_star, mode="max_eps", t=t)
        if not r["ok"]:
            return False, 0.0, None
        return r["eps"] > EPS_STRICT, r["eps"], r


# ---------------------------------------------------------------------------
# min-max driver over all structural partitions
# ---------------------------------------------------------------------------

def distinct_machines(P):
    return sorted(set(P), reverse=True)


def minmax_profile(c, n, verbose=True, extra_vectors=None, tol_kill=0.0):
    """Compute min over structural partitions P of sup_v C_P(v)/OPT(v).

    Exact (MILP-based, no bisection). tol_kill: margin when testing
    'ratio(P) >= current_min' (test at current_min - tol_kill).
    Returns dict with minmax value, best partition, witnesses, stats.
    """
    import time
    t0 = time.time()
    c = tuple(c)
    k = len(c)
    m = sum(c)
    kill = KillMILP(c, n)
    parts = gen_partitions(c, n)
    P_arr = partitions_array(parts, n, k)
    nP = len(parts)
    lib = make_library(k, n)
    if extra_vectors:
        lib += [np.asarray(v, float) for v in extra_vectors]
    LB = eval_vectors(P_arr, lib)
    witnesses = list(lib)          # global pool of value vectors (for LB bumps)

    def add_witness(v):
        witnesses.append(np.asarray(v, float))
        np.maximum(LB, eval_vectors(P_arr, [witnesses[-1]]), out=LB)

    order = np.argsort(LB, kind="stable")
    current_min = np.inf
    best_idx = None
    best_info = None               # (M*, solve_result of min_s)
    n_milp_partitions = 0
    n_kill_milp = 0

    for cnt, idx in enumerate(order):
        if LB[idx] >= current_min - 1e-12:
            continue
        P = parts[idx]
        # kill test: is ratio(P) >= current_min ?
        t_test = current_min - tol_kill
        killed = False
        for M in distinct_machines(P):
            n_kill_milp += 1
            if kill.killed_at(M, t_test):
                killed = True
                break
        if killed:
            LB[idx] = max(LB[idx], current_min)
            continue
        # full exact evaluation of this partition
        n_milp_partitions += 1
        ratio = -np.inf
        info = None
        for M in distinct_machines(P):
            r = kill.sup_ratio(M)
            if r["ratio"] > ratio:
                ratio = r["ratio"]
                info = (M, r)
        ratio = max(ratio, 1.0)
        LB[idx] = max(LB[idx], ratio)
        add_witness(info[1]["v"])   # adversarial witness vector for this P
        if ratio < current_min - 1e-12:
            current_min = ratio
            best_idx = idx
            best_info = info
            if verbose:
                print(f"  [{time.time()-t0:7.1f}s] new min {current_min:.6f} "
                      f"at P={partition_str(parts[idx])} (scanned {cnt+1}/{nP})",
                      flush=True)
    return {
        "profile": c, "n": n, "k": k, "m": m,
        "minmax": current_min,
        "best_partition": parts[best_idx] if best_idx is not None else None,
        "best_info": best_info,
        "num_partitions": nP,
        "partitions_fully_evaluated": n_milp_partitions,
        "kill_milp_calls": n_kill_milp,
        "LB": LB,
        "parts": parts,
        "witnesses": witnesses,
        "time": time.time() - t0,
    }


def packing_str(assign, ranks):
    """assign: bin index per labeled job; ranks: rank (0-based) per job."""
    nb = assign.max() + 1
    bins = [[] for _ in range(nb)]
    for j, b in enumerate(assign):
        bins[b].append(ranks[j] + 1)
    return " | ".join("{" + ",".join(map(str, sorted(bb))) + "}" for bb in bins)


def witness_report(c, n, P):
    """For a given partition P: per distinct machine, exact sup ratio,
    strict-attainability, witness v and OPT packing."""
    kill = KillMILP(c, n)
    out = []
    for M in distinct_machines(P):
        r = kill.sup_ratio(M)
        R = r["ratio"]
        att, eps, wr = kill.strict_attained(M, R)
        rec = {"machine": machine_str(M), "ratio": R, "attained_strict": att,
               "eps": eps, "v_weak": r["v"], "packing_weak": r["assign"]}
        if wr is not None:
            rec["v_strict"] = wr["v"]
            rec["packing_strict"] = wr["assign"]
        if not att:
            # strict witness slightly below R
            att2, eps2, wr2 = kill.strict_attained(M, R - 1e-5)
            rec["strict_below"] = (R - 1e-5, eps2,
                                   wr2["v"] if wr2 else None,
                                   wr2["assign"] if wr2 else None)
        out.append(rec)
    return out
