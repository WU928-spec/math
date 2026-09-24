"""main_b4eq_probe.py —— B4 逃逸 b 取等格 CEGAR 探针。
LP：值语言角落（V.build 默认行）+ A5+LZ/HZ + B4_q 破（j_{q+2}+s_{nS+1-q} > 1）
+ 取等 r∈{q,q+1}（j_q+s_{nS+1-q} <= 1，即 r>=q）。
q = nS−k（T2 用法），k 取 uncond 层（k ≤ m−2a−2）。
逐见证判：真角落（assign_juniors）/ 可达（fallback_event）/ 可装箱（packs_into_m）。
全死 ⟹ 逃逸 b 在角落域空 ⟹ B4 单行合法性闭合（最后一击）。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V
from main_cegar3 import MG
from main_phantom_corner import assign_juniors
from main_reach_pack2 import packs_into_m
from toolbox import fallback_event

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_b4eq_probe.jsonl')


def build(m, cnt, k):
    nS = m - 1
    q = nS - k
    A, bc, bt, names, leg, nv = V.build(m, cnt)
    A, bc, bt = list(A), list(bc), list(bt)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    for i in range(1, k + 1):
        row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        A.append(row); bc.append(-MG); bt.append(F(0))
    row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    A.append(row); bc.append(F(0)); bt.append(F(0))
    if k < nS:
        row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        A.append(row); bc.append(-MG); bt.append(F(0))
    # B4_q 破：j_{q+2} + s_{nS+1-q} > 1  ⟺  -j_{q+2} - s_{nS+1-q} <= -1-MG
    row = [F(0)] * nv
    row[vj(q + 2)] = -1; row[vs(nS + 1 - q)] = -1
    A.append(row); bc.append(-1 - MG); bt.append(F(0))
    # 取等 r>=q：j_q + s_{nS+1-q} <= 1
    row = [F(0)] * nv
    row[vj(q)] = 1; row[vs(nS + 1 - q)] = 1
    A.append(row); bc.append(F(1)); bt.append(F(0))
    return A, bc, bt, nv, q


def main():
    pf = open(OUT, 'w')
    n_wit = n_corner = n_reach = n_pack = 0
    for m in range(6, 15):
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            a = cnt[0]
            for k in range(2, m - 2 * a - 1):  # uncond 层 k ≤ m−2a−2
                A, bc, bt, nv, q = build(m, cnt, k)
                Af = np.array([[float(x) for x in row] for row in A])
                bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
                nS = m - 1
                rng = np.random.default_rng(m * 101 + k)
                hit = False
                for t0 in [0.28, 0.30, 0.32, 1 / 3]:
                    for _ in range(3):
                        c = rng.standard_normal(nv)
                        res = linprog(c=c, A_ub=Af, b_ub=bcf + btf * t0, bounds=(None, None), method='highs')
                        if res.status != 0:
                            continue
                        x = res.x
                        p = x[0]; s = list(x[3:3 + nS]); j = list(x[3 + nS:3 + 2 * nS])
                        n_wit += 1
                        hit = True
                        ok, kk, assign, reason = assign_juniors(s, j, p, t0, s[0], j[-1])
                        if ok:
                            n_corner += 1
                            seq = sorted([p] + s, reverse=True) + sorted(j + [t0], reverse=True)
                            ev = fallback_event(seq, m)
                            if ev is not None:
                                n_reach += 1
                                if packs_into_m([p] + s + j + [t0], m):
                                    n_pack += 1
                                    print(f'**取等格可装箱! m={m} cnt={cnt} k={k} q={q} t={t0:.3f}')
                                    print(f'   s={np.round(s,3)}\n   j={np.round(j,3)}')
                if hit:
                    pf.write(json.dumps({'m': m, 'cnt': cnt, 'k': k, 'q': q}) + '\n')
        print(f'm={m} 完成（见证 {n_wit} 真角落 {n_corner} 可达 {n_reach} 可装箱 {n_pack}）', flush=True)
    print(f'\n判决：见证 {n_wit}、真角落 {n_corner}、可达 {n_reach}、可装箱 {n_pack}')


if __name__ == '__main__':
    main()
