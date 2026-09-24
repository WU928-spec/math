"""main_cegar1.py —— CEGAR 第 1 轮：新合法行"低端区配对支配"（mon2+pair ⟹ j_{nS-k+i} >= p-s_i, i=1..k）。
合法性证明（角落必要）：低端区机器 1..k（senior 升序）经 mon2 收 junior 升序，机器 i 得
选中 k 件中第 i 小者 chosen_i；chosen_i >= p-s_i+MG（pair 严格）；k 件最大者按分量
支配任意 k 件 ⟹ j_{nS-k+i} >= chosen_i >= p-s_i+MG。∎（含 fs：i=k 时 j_{nS}>=p-s_k+MG）
在 agent-1 值语言 build 基础上加本行（A5），重扫 m=6..16 × 两 cnt × 全 k，固定 t 网格。
判决：FEAS 收敛到 0 ⟹ open 段值语言 LP 闭合候选（转精确证书）；仍有 FEAS ⟹ 幻影喂回 CEGAR。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V

MG = F(1, 10000)


def build_with_a5(m, cnt, k):
    """agent-1 build + A5 低端区配对支配行（k 固定=jj+1）。"""
    nS = m - 1
    A, bc, bt, names, leg, nv = V.build(m, cnt)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1)
    vj = lambda r: 3 + nS + (r - 1)
    for i in range(1, k + 1):
        row = [F(0)] * nv
        row[IP] = 1
        row[vs(i)] = -1
        row[vj(nS - k + i)] = -1
        A.append(row)          # p - s_i - j_{nS-k+i} <= -MG  ⟺  j >= p - s_i + MG
        bc.append(-MG)
        bt.append(F(0))
        names.append(f'A5_{i}')
        leg.append('mon2+pair: 低端机 i 得第 i 小选中 junior >= p-s_i; k 件最大者分量支配')
    return A, bc, bt, names, leg, nv


def main():
    tmesh = [0.27, 0.29, 0.30, 0.31, 0.32, 0.33, 1 / 3]
    ninf = nfeas = 0
    for m in range(6, 17):
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            for k in range(2, m - 2):  # open 段
                A, bc, bt, names, leg, nv = build_with_a5(m, cnt, k)
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
                    print(f'  FEAS@t={found:.3f} m={m} cnt={cnt} k={k}', flush=True)
            print(f'm={m} cnt={cnt[:3]} 扫完（INF {ninf} FEAS {nfeas}）', flush=True)
    print(f'\n判决：INF {ninf} / FEAS {nfeas}')


if __name__ == '__main__':
    main()
