"""G1-razor 判决: 39 个 sjrev 承重点见证上检验
 (b) 可装箱? (c) 存在 SS={s1,s2}(两最小 senior) 的装箱?
 反例形态 = (b)真 且 (c)假。 witnessing 用 main_cegar3.build_k 去 SJrev 行。
"""
import numpy as np, sys, os, json
from functools import lru_cache
from itertools import combinations
from scipy.optimize import linprog
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import a1_value_lp2 as V
from main_cegar3 import build_k

def feas_typed(s, pool, cnt, force_ss12=False):
    """mask DP 可装箱判定。force_ss12: 强制 SS 对=值序最小两 senior(先放置, a-1)。p 独箱在外。"""
    nS = len(s)
    items = list(s) + list(pool)
    n = len(items)
    a, b, c, d, e, f = cnt
    if force_ss12:
        order = np.argsort(np.array(s))
        i1, i2 = int(order[0]), int(order[1])
        if s[i1] + s[i2] > 1 + 1e-9:
            return False
        rem = [i for i in range(nS) if i not in (i1, i2)]
        # 剩余 senior 重编号(保持 s/j 分界: senior 0..nS-3, pool 索引平移)
        ns2 = nS - 2
        s2 = [s[i] for i in rem]
        pool2 = list(pool)
        items2 = s2 + pool2
        n2 = len(items2)
        @lru_cache(maxsize=None)
        def dfs2(mask, a, b, c, d, e, f):
            if mask == 0: return True
            i = (mask & (-mask)).bit_length() - 1
            is_s = i < ns2
            rest = mask ^ (1 << i)
            others = []
            mm = rest
            while mm:
                lsb = mm & (-mm); others.append(lsb.bit_length() - 1); mm ^= lsb
            for r in (0, 1, 2):
                for extra in combinations(others, r):
                    nsx = is_s + sum(1 for x in extra if x < ns2)
                    nj = (1 + r) - nsx
                    sm = items2[i] + sum(items2[x] for x in extra)
                    if sm > 1 + 1e-9: continue
                    na, nb, nc, nd, ne, nf = a, b, c, d, e, f
                    if (nsx, nj) == (2, 0) and a > 0: na -= 1
                    elif (nsx, nj) == (1, 1) and b > 0: nb -= 1
                    elif (nsx, nj) == (1, 0) and c > 0: nc -= 1
                    elif (nsx, nj) == (0, 3) and d > 0: nd -= 1
                    elif (nsx, nj) == (0, 2) and e > 0: ne -= 1
                    elif (nsx, nj) == (0, 1) and f > 0: nf -= 1
                    else: continue
                    if dfs2(rest ^ sum((1 << x) for x in extra), na, nb, nc, nd, ne, nf):
                        return True
            return False
        return dfs2((1 << n2) - 1, a - 1, b, c, d, e, f)
    @lru_cache(maxsize=None)
    def dfs(mask, a, b, c, d, e, f):
        if mask == 0: return True
        i = (mask & (-mask)).bit_length() - 1
        is_s = i < nS
        rest = mask ^ (1 << i)
        others = []
        mm = rest
        while mm:
            lsb = mm & (-mm); others.append(lsb.bit_length() - 1); mm ^= lsb
        for r in (0, 1, 2):
            for extra in combinations(others, r):
                nsx = is_s + sum(1 for x in extra if x < nS)
                nj = (1 + r) - nsx
                sm = items[i] + sum(items[x] for x in extra)
                if sm > 1 + 1e-9: continue
                na, nb, nc, nd, ne, nf = a, b, c, d, e, f
                if (nsx, nj) == (2, 0) and a > 0: na -= 1
                elif (nsx, nj) == (1, 1) and b > 0: nb -= 1
                elif (nsx, nj) == (1, 0) and c > 0: nc -= 1
                elif (nsx, nj) == (0, 3) and d > 0: nd -= 1
                elif (nsx, nj) == (0, 2) and e > 0: ne -= 1
                elif (nsx, nj) == (0, 1) and f > 0: nf -= 1
                else: continue
                if dfs(rest ^ sum((1 << x) for x in extra), na, nb, nc, nd, ne, nf):
                    return True
        return False
    return dfs((1 << n) - 1, a, b, c, d, e, f)

def witness(m, cnt, k, tmesh):
    A, bc, bt, names, leg, nv = build_k(m, cnt, k)
    # 去 SJrev 行
    idx = [i for i, nm in enumerate(names) if not nm.startswith('SJrev')]
    A2 = [A[i] for i in idx]; bc2 = [bc[i] for i in idx]; bt2 = [bt[i] for i in idx]
    Af = np.array([[float(x) for x in row] for row in A2])
    for t0 in tmesh:
        bf = np.array([float(bc2[i]) + float(bt2[i]) * t0 for i in range(len(A2))])
        res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bf, bounds=(None, None), method='highs')
        if res.status == 0:
            return t0, res.x
    return None, None

if __name__ == '__main__':
    tmesh = [0.29, 0.30, 0.31, 0.322, 1/3]
    sjrev = []
    for line in open('main_ablation_class.jsonl'):
        r = json.loads(line)
        if r.get('cls') == 'sjrev':
            sjrev.append((r['m'], tuple(r['cnt']), r['k']))
    print(f'sjrev 点 {len(sjrev)} 个')
    n_pack = n_g1 = n_counter = 0
    for m, cnt, k in sjrev:
        nS = m - 1
        t0, x = witness(m, cnt, k, tmesh)
        if x is None:
            print(f'm={m} {cnt} k={k}: 无见证'); continue
        s = list(x[3:3 + nS]); pool = list(x[3 + nS:3 + 2 * nS]) + [t0]
        p_ = x[0]
        b_ = feas_typed(s, pool, cnt)
        g_ = feas_typed(s, pool, cnt, force_ss12=True) if b_ else False
        n_pack += b_; n_g1 += g_
        if b_ and not g_:
            n_counter += 1
            print(f'** 反例候选 m={m} {cnt} k={k} t={t0:.3f}: 可装箱但最小2a-SS 不可', flush=True)
            print(f'   s={np.round(s,4)} pool={np.round(pool,4)} p={p_:.4f}')
    print(f'\n可装箱 {n_pack}/39, 其中 G1(最小2a-SS) 可行 {n_g1}, 反例 {n_counter}')
