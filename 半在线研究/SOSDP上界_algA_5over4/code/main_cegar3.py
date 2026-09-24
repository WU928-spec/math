"""main_cegar3.py —— CEGAR 第 3 轮：补情形定义行 LZ/HZ（k 由值唯一确定）。
LZ: 4s_k <= 5a_m+q_1（机器 k=jj 是最大低端机, s<=K-q1）
HZ: 4s_{k+1} >= 5a_m+q_1+MG（机器 k+1 是最小 hi 机, s>K-q1; k=nS 时无）
合法性：角落情形定义本身（机 LP 已审计 lowzone/hizone 同义行）。
叠加：agent-1 值语言全行 + A5（低端区配对支配）+ LZ/HZ，重扫 open 段固定 t 网格。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V

MG = F(1, 10000)


def build_k(m, cnt, k):
    """值语言全行 + A5(k) + LZ/HZ(k)。1-indexed: s_1..s_nS, j_1..j_nS。"""
    nS = m - 1
    A, bc, bt, names, leg, nv = V.build(m, cnt)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1)
    vj = lambda r: 3 + nS + (r - 1)

    def con(row, c0, c1, nm, proof):
        A.append([F(x) for x in row]); bc.append(F(c0)); bt.append(F(c1))
        names.append(nm); leg.append(proof)

    # A5: j_{nS-k+i} >= p - s_i + MG, i=1..k
    for i in range(1, k + 1):
        row = [F(0)] * nv
        row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        con(row, -MG, 0, f'A5_{i}', 'mon2+pair: 低端机 i 得第 i 小选中 junior>=p-s_i; k 件最大者分量支配')
    # LZ: 4 s_k - 5 a_m - q_1 <= 0
    row = [F(0)] * nv
    row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    con(row, 0, 0, 'LZ', '情形定义: s_k<=K-q1（机 k=jj 最大低端机）')
    # HZ: -4 s_{k+1} + 5 a_m + q_1 <= -MG（k<nS 时）
    if k < nS:
        row = [F(0)] * nv
        row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        con(row, -MG, 0, 'HZ', '情形定义: s_{k+1}>K-q1（机 k+1 最小 hi 机）')
    return A, bc, bt, names, leg, nv


def main():
    tmesh = [0.27, 0.29, 0.30, 0.31, 0.32, 0.33, 1 / 3]
    ninf = nfeas = 0
    for m in range(6, 17):
        mok = True
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            for k in range(2, m - 2):
                A, bc, bt, names, leg, nv = build_k(m, cnt, k)
                Af = np.array([[float(x) for x in row] for row in A])
                bcf = np.array([float(x) for x in bc])
                btf = np.array([float(x) for x in bt])
                found = None
                for t0 in tmesh:
                    res = linprog(c=np.zeros(nv), A_ub=Af, b_ub=bcf + btf * t0,
                                  bounds=(None, None), method='highs')
                    if res.status == 0:
                        found = t0
                        break
                if found is None:
                    ninf += 1
                else:
                    nfeas += 1
                    mok = False
                    print(f'  FEAS@t={found:.3f} m={m} cnt={cnt} k={k}', flush=True)
        print(f'm={m} 扫完（{"全 INF" if mok else "有 FEAS"}；累计 INF {ninf} FEAS {nfeas}）', flush=True)
    print(f'\n判决：INF {ninf} / FEAS {nfeas}')


if __name__ == '__main__':
    main()
