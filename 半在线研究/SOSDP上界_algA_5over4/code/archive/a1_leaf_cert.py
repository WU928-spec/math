"""E 方向1+2(采样版): 叶 dominance 证书(数值) + LP 剪枝后有效叶数。
dominance 判定: canonical 箱和向量 按分量 <= 大量随机装箱的箱和向量(CDL 叶版)。
"""
import numpy as np, itertools, sys, os
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hole_close import build_close
from a1_swap_tree import corner_point

def rand_pack_vec(items, m, rng, cap=1.0):
    """随机装箱: shuffle 后 first-fit-decreasing 变体, 返回排序箱和向量。"""
    it = list(items); rng.shuffle(it)
    it.sort(reverse=True)
    bins = []
    for w in it:
        placed = False
        order = sorted(range(len(bins)), key=lambda i: bins[i])
        for i in order:
            if bins[i] + w <= cap + 1e-9:
                bins[i] += w; placed = True; break
        if not placed:
            if len(bins) >= m: return None
            bins.append(w)
    return tuple(sorted(bins, reverse=True))

def leaf_cert_check(m, cnt, k, t0, n_sample=300, seed=0):
    nS = m - 1; jj = k - 1
    st, x = corner_point(m, cnt, k, t0)
    if st != 0: return None
    items0 = list(x[:2 + 2 * nS])
    hi = list(range(jj + 1, nS))
    j_idx = [2 + nS + i for i in hi]
    jvals = [x[i] for i in j_idx]
    A, bc, bt, names, nv = build_close(m, cnt, k, use_mon2=False, use_ammin=False)
    Af = np.array([[float(z) for z in row] for row in A])
    bcf = np.array([float(c) for c in bc]); btf = np.array([float(v) for v in bt])
    rng = np.random.default_rng(seed)
    total = alive = cert_ok = 0
    for perm in itertools.permutations(range(len(hi))):
        total += 1
        items = list(items0)
        for slot, src in enumerate(perm):
            items[j_idx[slot]] = jvals[src]
        rows = []; rhs = []
        for slot, src in enumerate(perm):
            r = np.zeros(nv); r[j_idx[slot]] = 1
            rows.append(r); rhs.append(jvals[src])
        res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bcf + btf * t0,
                      A_eq=np.vstack(rows) if rows else None,
                      b_eq=np.array(rhs) if rows else None,
                      bounds=(None, None), method='highs')
        if res.status != 0: continue
        alive += 1
        # canonical 向量
        p_, t_ = items[0], items[1]
        s = sorted(items[2:2 + nS]); j = list(items[2 + nS:2 + 2 * nS]) + [t_]
        a, b, c, d, e, f = cnt
        bins = [[p_]]
        for i in range(a): bins.append([s[2*i], s[2*i+1]])
        for i in range(b): bins.append([s[2*a+i], j[i]])
        si = b
        for i in range(d): bins.append([j[si], j[si+1], j[si+2]]); si += 3
        for i in range(e): bins.append([j[si], j[si+1]]); si += 2
        if not all(sum(bb) <= 1 + 1e-9 for bb in bins):
            continue
        canon = sorted((sum(bb) for bb in bins), reverse=True)
        ok = True
        for _ in range(n_sample):
            v = rand_pack_vec(list(items), m, rng)
            if v is None: continue
            vv = list(v) + [0.0] * (len(canon) - len(v))
            if not all(canon[i] <= vv[i] + 1e-6 for i in range(len(canon))):
                ok = False; break
        cert_ok += ok
    return total, alive, cert_ok

if __name__ == '__main__':
    for m, cnt, ks in [(18, (3, 11, 0, 1, 2, 0), [15, 16]),
                       (24, (4, 17, 0, 2, 1, 1), [20, 21])]:
        for k in ks:
            for t0 in [0.322, 0.328]:
                r = leaf_cert_check(m, cnt, k, t0)
                if r is None:
                    print(f'm={m} k={k} t={t0}: LP 不可行', flush=True); continue
                print(f'm={m} k={k} t={t0}: 叶={r[0]} 存活={r[1]} 剪枝={100*(1-r[1]/max(r[0],1)):.0f}% '
                      f'dom采样证={r[2]}/{r[1]}', flush=True)
