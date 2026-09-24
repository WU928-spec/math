"""实质隔离全 t 网格：corner(use_b4=False, sjrev=True) + A5/LZ/HZ + B4破 + 取等行。
判定：对每个 uncond 配置，若 ∃t∈网格使 LP 可行 ⟹ 该配置无 t-uniform 证书（step3 对该配置失守）。"""
import sys
sys.path.insert(0, 'code')
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F
import a1_value_lp2 as V

MG_ = F(1, 10000)
tmesh = [0.27, 0.29, 0.30, 0.31, 0.32, 1/3]

def build(m, cnt, k):
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_b4=False, use_sjrev=True)
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

n_cfg = n_allinf = 0
bad = []
for m in range(6, 17):
    nS = m - 1
    for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
        a = cnt[0]
        for k in range(2, m - 2 * a - 1):
            q = nS - k
            if not (2 * a + 1 <= q <= nS - 2):
                continue
            for rq_tag, rq in [('e0', q), ('e1', q - 2)]:
                A, bc, bt, nv, vs, vj, nS_ = build(m, cnt, k)
                row = [F(0)] * nv; row[vj(q + 2)] = -1; row[vs(nS + 1 - q)] = -1
                A.append(row); bc.append(-1 - MG_); bt.append(F(0))
                if rq >= 1:
                    row = [F(0)] * nv; row[vj(rq)] = 1; row[vs(nS + 1 - q)] = 1
                    A.append(row); bc.append(F(1)); bt.append(F(0))
                Af = np.array([[float(x) for x in row] for row in A])
                bf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
                feas_t = []
                for t0 in tmesh:
                    if t0 <= float(F(m - 1, 4 * (m - 2))):
                        continue
                    res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bf + btf * t0,
                                  bounds=(None, None), method='highs')
                    if res.status == 0:
                        feas_t.append(round(t0, 4))
                n_cfg += 1
                if not feas_t:
                    n_allinf += 1
                else:
                    bad.append((m, cnt[0], k, q, rq_tag, feas_t))
print(f'总判定 {n_cfg}（配置×族），全 t 网格不可行 {n_allinf}，存在可行 t 的 {len(bad)}')
for b_ in bad[:30]:
    print(b_)
