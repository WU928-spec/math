"""senior 分割 w.l.o.g. 检验 v2: 用 main_jjj_enum 的行基建(rows_fixed+squeeze+pair+SS01)
取 open 点, 枚举全部 typed 装箱, 检验"可装箱 ⟹ 存在最小 2a 为 SS 对的装箱"。
"""
import numpy as np, sys, os, itertools, json
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main_jjj_enum import base_rows, pair_row, ss01_row

def open_point(m, cnt, k, pair, use_ss01=True):
    R, nv, nS = base_rows(m, cnt, k)
    R = R + [pair_row(nv, nS, pair[0], pair[1])]
    if use_ss01:
        R = R + [ss01_row(nv)]
    A = np.array([r[0] for r in R])
    for t0 in [0.27, 0.29, 0.30, 0.31, 0.32, 0.326, 0.329]:
        b = np.array([float(r[1]) + float(r[2]) * t0 for r in R])
        res = linprog(c=np.zeros(nv), A_ub=A, b_ub=b, bounds=(None, None), method='highs')
        if res.status == 0:
            x = res.x
            return t0, list(x[2:2 + nS]), list(x[2 + nS:2 + 2 * nS])
    return None

def all_packings_typed(s, pool, cnt):
    nS = len(s); items = list(s) + list(pool); n = len(items)
    a, b, c, d, e, f = cnt
    sols = []
    def dfs(mask, bins, a, b, c, d, e, f):
        if mask == 0:
            sols.append(list(bins)); return
        i = (mask & (-mask)).bit_length() - 1
        is_s = i < nS
        rest = mask ^ (1 << i)
        others = []
        mm = rest
        while mm:
            lsb = mm & (-mm); others.append(lsb.bit_length() - 1); mm ^= lsb
        for r in (0, 1, 2):
            for extra in itertools.combinations(others, r):
                ns = is_s + sum(1 for x in extra if x < nS)
                nj = (1 + r) - ns
                sm = items[i] + sum(items[x] for x in extra)
                if sm > 1 + 1e-9: continue
                na, nb, nc, nd, ne, nf = a, b, c, d, e, f
                if (ns, nj) == (2, 0) and a > 0: na -= 1
                elif (ns, nj) == (1, 1) and b > 0: nb -= 1
                elif (ns, nj) == (1, 0) and c > 0: nc -= 1
                elif (ns, nj) == (0, 3) and d > 0: nd -= 1
                elif (ns, nj) == (0, 2) and e > 0: ne -= 1
                elif (ns, nj) == (0, 1) and f > 0: nf -= 1
                else: continue
                dfs(rest ^ sum((1 << x) for x in extra), bins + [(i,) + extra],
                    na, nb, nc, nd, ne, nf)
    dfs((1 << n) - 1, [], a, b, c, d, e, f)
    return sols

def ss_sets(pack, nS):
    return frozenset(x for bin_ in pack for x in bin_
                     if x < nS and len([y for y in bin_ if y < nS]) == 2 and len(bin_) == 2)

if __name__ == '__main__':
    cases = [(7, (1, 4, 0, 1, 0, 0), 3, (3, 4)),
             (7, (2, 2, 0, 1, 1, 0), 3, (3, 4)),
             (8, (1, 5, 0, 1, 0, 0), 2, (2, 3)),
             (8, (2, 3, 0, 1, 1, 0), 4, (4, 5)),
             (8, (1, 5, 0, 1, 0, 0), 3, (3, 4))]
    for m, cnt, k, pair in cases:
        nS = m - 1
        pt = open_point(m, cnt, k, pair)
        if pt is None:
            print(f'm={m} cnt={cnt} k={k} pair={pair}: 无点'); continue
        t0v, s, pool = pt
        pool = pool + [t0v]
        sols = all_packings_typed(s, pool, cnt)
        a = cnt[0]
        smallest = frozenset(range(2 * a))
        wl = [p for p in sols if ss_sets(p, nS) == smallest]
        n_counter = sum(1 for p in sols if ss_sets(p, nS) != smallest)
        print(f'm={m} cnt={cnt} k={k} t={t0v:.3f}: 装箱 {len(sols)}, '
              f'最小2a-SS {len(wl)}, 非最小 {n_counter} -> {"w.l.o.g. 成立" if not n_counter else "反例!"}', flush=True)
