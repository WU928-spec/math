"""a3_ (P) 兼容计数账配平探测仪（子线1）。
聚合变量：p,t,q1,am,S_lo,S_hi,J_lo,J_hi（低端区 k=jj+1 台、高端区 m-1-k 台）。
坍缩输入（中段结构定理）：低端 junior 全 >1-2t ⟹ J_lo>k(1-2t)。
装箱容量：S+J+t<=m-1；pair 汇总 S+J>=(m-1)p。
配平 LP：非负权组合使变量列全消、常数和<0 ⟺ (P) 聚合层可证。
"""
import numpy as np
from scipy.optimize import linprog
from fractions import Fraction as F


def balance(m, k, extra_rows=()):
    V = ['p', 't', 'q1', 'am', 'S_lo', 'S_hi', 'J_lo', 'J_hi']
    # 行 = Σ coeff·var + const >= 0；S = S_lo+S_hi, J = J_lo+J_hi
    nS = m - 1
    ING = [
        ('danger', {'p': 1, 't': 1}, F(-5, 4)),
        ('CapV', {'S_lo': -1, 'S_hi': -1, 'J_lo': -1, 'J_hi': -1, 't': -1}, F(m - 1)),
        ('PairV', {'S_lo': 1, 'S_hi': 1, 'J_lo': 1, 'J_hi': 1, 'p': -nS}, F(0)),
        # 低端区 senior <= K-q1 = (5am+q1)/4：S_lo <= k(5am+q1)/4
        ('Slo_cap', {'S_lo': -1, 'am': F(5 * k, 4), 'q1': F(k, 4)}, F(0)),
        # 高端区 senior > K-q1：S_hi >= (nS-k)(5am+q1)/4
        ('Shi_fl', {'S_hi': 1, 'am': -F(5 * (nS - k), 4), 'q1': -F(nS - k, 4)}, F(0)),
        # 坍缩：低端 junior > 1-2t：J_lo > k(1-2t)
        ('Jlo_fl', {'J_lo': 1, 't': -2 * k}, F(-k)),
        # 高端 junior >= t
        ('Jhi_fl', {'J_hi': 1, 't': -(nS - k)}, F(0)),
        # senior 非小：S >= nS(1-2t)
        ('S_fl', {'S_lo': 1, 'S_hi': 1, 't': -2 * nS}, F(-nS)),
        ('am>=q1', {'am': 1, 'q1': -1}, F(0)),
        ('q1>=t', {'q1': 1, 't': -1}, F(0)),
        ('q1<=2t', {'q1': -1, 't': 2}, F(0)),
        ('L<=1', {'am': -1, 'q1': -1}, F(1)),
        # junior 上界：J <= nS·q1
        ('J_cap', {'J_lo': -1, 'J_hi': -1, 'q1': nS}, F(0)),
        # p<K：p <= (5/4)(am+q1)
        ('pK', {'p': -1, 'am': F(5, 4), 'q1': F(5, 4)}, F(0)),
        # p<=1
        ('p<=1', {'p': -1}, F(1)),
    ]
    ING.extend(extra_rows)
    nI = len(ING)
    nv = len(V)
    Aeq = np.zeros((nv, nI))
    for j, (nm, d, c) in enumerate(ING):
        for v, w in d.items():
            Aeq[V.index(v), j] = float(w)
    Aub = np.array([[float(c) for _, _, c in ING]])
    res = linprog(c=np.zeros(nI), A_eq=Aeq, b_eq=np.zeros(nv),
                  A_ub=Aub, b_ub=[-1.0], bounds=(0, None), method='highs')
    return res, ING, V, Aeq


def main():
    print('兼容计数账配平（坍缩版）：status 0=配平成功/(P)聚合层可证, 2=不可行/障碍')
    for m in [8, 12, 16, 20]:
        row = []
        for k in range(2, m - 1):
            res, ING, V, Aeq = balance(m, k)
            row.append('✓' if res.status == 0 else '✗')
        print(f'  m={m}: k=2..{m-2}: {" ".join(row)}')
    # 提取一个成功例的权（若有）
    for m, k in [(12, 5), (12, 6), (16, 8), (20, 10)]:
        res, ING, V, Aeq = balance(m, k)
        if res.status == 0:
            w = res.x
            wf = [F(float(v)).limit_denominator(10**6) for v in w]
            for j in range(len(V)):
                s = sum(F(Aeq[j, i].item()).limit_denominator(10**9) * wf[i] for i in range(len(ING)))
                assert s == 0, (V[j], s)
            cst = sum(ING[i][2] * wf[i] for i in range(len(ING)))
            print(f'  ✓ 恒等式存在 m={m} k={k}: 常数和={cst}<0；权:',
                  {ING[i][0]: str(wf[i]) for i in range(len(ING)) if wf[i] != 0})


if __name__ == '__main__':
    main()
