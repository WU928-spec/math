import sys, os
sys.path.insert(0, 'code')
from fractions import Fraction as F
import a1_value_lp2 as V
import main_cegar3 as C

m, cnt, k, q = 8, (1, 5, 0, 1, 0, 0), 3, 4
A, bc, bt, names, leg, nv = C.build_k(m, cnt, k)
nS = m - 1
vs = lambda r: 3 + (r - 1)
vj = lambda r: 3 + nS + (r - 1)

def con(row, c0, c1, nm):
    A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1)); names.append(nm)
z = [F(0)] * nv
# B4_q 破：-j_{q+2} - s_{nS+1-q} <= -1-MG
r_ = list(z); r_[vj(q + 2)] = -1; r_[vs(nS + 1 - q)] = -1
con(r_, -1 - F(1, 10000), 0, 'B4broken')
# 取等 r>=q：j_q + s_{nS+1-q} <= 1
r_ = list(z); r_[vj(q)] = 1; r_[vs(nS + 1 - q)] = 1
con(r_, 1, 0, 'req_q')

# E.4 权重（分母 5033）
w = {'jrt1': 100000, 'jrt5': 150000, 'jrt6': 180000, 'danger': 300000,
     'j1>=t': 200000, 'jmax<=q1': 180000, 'q1<=am': 150000, 'B1_SS01': 150000,
     'B2_JJJ01': 100000, 'B4_q4': 120000, 'A5_1': 150000, 'A5_2': 150000, 'HZ': 30000}
# 名称对齐：E.4 的 "B4_q4" 应为 B4broken（情形假设行）；"j1>=t" 在 V.build 中名 'j1>=t'
name_map = {'B4_q4': 'B4broken'}
cols = {}
for nm, wt in w.items():
    nm2 = name_map.get(nm, nm)
    idxs = [i for i, n in enumerate(names) if n == nm2]
    print(f'{nm:10s} -> {nm2:10s} matches={len(idxs)}')
    for i in idxs:
        cols[i] = wt

# 计算 A^T y, b_c^T y, b_t^T y
from collections import defaultdict
acc = defaultdict(F)
bcy, bty = F(0), F(0)
for i, wt in cols.items():
    for v in range(nv):
        if A[i][v] != 0:
            acc[v] += F(wt) * A[i][v] / F(5033)
    bcy += F(wt) * bc[i] / F(5033)
    bty += F(wt) * bt[i] / F(5033)
bad = {v: c for v, c in acc.items() if c != 0}
print('nonzero A^Ty cols:', bad if bad else 'NONE (balanced)')
print('b_c^T y =', bcy, '=', float(bcy))
print('b_t^T y =', bty, '=', float(bty))
