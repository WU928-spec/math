"""变体：corner(use_b4=False, use_sjrev=True) + A5/LZ/HZ + B4破 + 取等 的可行性。
另测：SJrev 行单独承重（去 B4 后 SJrev 是否杀 164 配置）。"""
import sys
sys.path.insert(0, 'code')
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import a1_value_lp2 as V

MG_ = F(1, 10000)

def build(m, cnt, k, sjrev):
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_b4=False, use_sjrev=sjrev)
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

for sjrev in [True, False]:
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
                A, bc, bt, nv, vs, vj, nS_ = build(m, cnt, k, sjrev)
                row = [F(0)] * nv; row[vj(q + 2)] = -1; row[vs(nS + 1 - q)] = -1
                A.append(row); bc.append(-1 - MG_); bt.append(F(0))
                row = [F(0)] * nv; row[vj(q)] = 1; row[vs(nS + 1 - q)] = 1
                A.append(row); bc.append(F(1)); bt.append(F(0))
                Af = np.array([[float(x) for x in row] for row in A])
                b = np.array([float(x) for x in bc]) + np.array([float(x) for x in bt]) * 0.30
                res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=b, bounds=(None, None), method='highs')
                if res.status == 0:
                    n_feas += 1; feas_list.append((m, cnt[0], k, q))
                else:
                    n_inf += 1
    print(f'sjrev={sjrev}: INFEASIBLE={n_inf} FEASIBLE={n_feas}')
    print('  feasible sample:', feas_list[:20])
