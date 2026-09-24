"""JEL 第①段实测: 用 a1_swap_tree 的 m=18 鬼影角落点(packable)做 JEL 下降三指标。"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from a1_swap_tree import corner_point
from a1_jel_seg1 import canonical_bins
from a1_jel_seg1 import descent, bin_type, key_of
from collections import Counter

m, cnt, k, t0 = 18, (3, 11, 0, 1, 2, 0), 15, 0.328
nS = m - 1
st, x = corner_point(m, cnt, k, t0)
assert st == 0
items = list(x[:2 + 2 * nS])
big_set = set(items[2:2 + nS])
can = canonical_bins(items, m, cnt)
assert all(sum(b) <= 1 + 1e-9 for b in can), 'canonical 不可装?'
rng = np.random.default_rng(3)
n = term = uniq = styp = 0
for trial in range(10):
    # 起点1: canonical; 起点2: 随机扰动(canonical 基础上)
    b0 = [list(b) for b in can]
    p_c, t_c, _ = descent(b0, big_set)
    b1 = None
    for _ in range(30):
        cand = [list(b) for b in can]
        for _ in range(3):
            i, j = rng.integers(0, len(cand), 2)
            if i != j and cand[i] and cand[j]:
                xi = cand[i].pop(); xj = cand[j].pop()
                cand[i].append(xj); cand[j].append(xi)
        if all(sum(b) <= 1 + 1e-9 for b in cand):
            b1 = cand; break
    if b1 is None: continue
    p_r, t_r, _ = descent(b1, big_set)
    n += 1; term += (t_c and t_r)
    uniq += (key_of(p_c) == key_of(p_r))
    tc = tuple(sorted(Counter(bin_type(b, big_set) for b in p_c).items()))
    tr = tuple(sorted(Counter(bin_type(b, big_set) for b in p_r).items()))
    styp += (tc == tr)
print(f'm=18 k=15 t={t0}: 实例{n} 终止{term}/{n} 双起点同极小{uniq}/{n} 极小同型{styp}/{n}')
print('极小形箱型:', tc)
