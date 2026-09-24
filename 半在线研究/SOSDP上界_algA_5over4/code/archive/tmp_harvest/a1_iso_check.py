"""隔离检验：corner(use_b4=False) + A5/LZ/HZ + B4破 + 取等行 的可行性（111+45 配置域）。
FEASIBLE = 取等格 step-3 对该配置非实质（退化）；INFEASIBLE = 实质。"""
import sys
sys.path.insert(0, 'code')
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import a1_value_lp2 as V

def build_iso(m, cnt, k):
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_b4=False, use_sjrev=False)
    nS = m - 1
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    A, bc, bt = list(A), list(bc), list(bt)
    def con(row, c0, c1):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1))
    for i in range(1, k + 1):
        row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        con(row, -MG_, 0)
    row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    con(row, 0, 0)
    if k < nS:
        row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        con(row, -MG_, 0)
    return A, bc, bt, nv, vs, vj, nS

MG_ = F(1, 10000)
n_inf = n_feas = 0
feas_list = []
for m in range(6, 17):
    nS = m - 1
    for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
        a = cnt[0]
        for k in range(2, m - 2 * a - 1):
            q = nS - k
            if not (2 * a + 1 <= q <= nS - 2):
                continue
            A, bc, bt, nv, vs, vj, nS_ = build_iso(m, cnt, k)
            # B4 破 + 取等 r>=q（e=0）；e=1 用 r>=q-2（j_{q-2}+s_{nS+1-q}<=1）
            for tag, rq in [('e0', q), ('e1', q - 2)]:
                A2 = list(A); bc2 = list(bc); bt2 = list(bt)
                row = [F(0)] * nv; row[vj(q + 2)] = -1; row[vs(nS + 1 - q)] = -1
                A2.append(row); bc2.append(-1 - MG_); bt2.append(F(0))
                if rq >= 1:
                    row = [F(0)] * nv; row[vj(rq)] = 1; row[vs(nS + 1 - q)] = 1
                    A2.append(row); bc2.append(F(1)); bt2.append(F(0))
                Af = np.array([[float(x) for x in row] for row in A2])
                b = np.array([float(x) for x in bc2]) + np.array([float(x) for x in bt2]) * 0.30
                res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=b, bounds=(None, None), method='highs')
                if res.status == 0:
                    n_feas += 1
                    feas_list.append((m, cnt[0], k, q, tag))
                else:
                    n_inf += 1
print('INFEASIBLE(实质):', n_inf, ' FEASIBLE(退化):', n_feas)
print('FEASIBLE 配置:', feas_list[:40])
