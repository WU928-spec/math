"""main_sliver_region.py —— 未决值区 CEGAR 核杀（agent-1 移交）。
两格：
  α'分支2: corner+sliver+s_{nS}>=J+t in (5/16,1/3]+J>=2p-4t —— 期望：见证全不可装箱/不可达
           （若可达且可装箱=G1 反例，立即告警）
  β:       corner+sliver+s_{nS}<J+t in (5/16,1/3] —— 检查 canonical 残差（SS={s1,s2},
           JJJ={t,j1,j2}，残差反序<=1）是否在见证上恒可行。
输出 main_sliver_region.jsonl。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V
from main_cegar3 import MG
from main_phantom_corner import check_packing
from main_reach_pack2 import packs_into_m
from toolbox import fallback_event

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_sliver_region.jsonl')


def build(m, cnt, k, cell):
    nS = m - 1
    A, bc, bt, names, leg, nv = V.build(m, cnt, use_sjrev=False, use_s1v=False, use_jjrev=False)
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
    # sliver: j1+j2+j3 > 1
    row = [F(0)] * nv
    row[vj(1)] = -1; row[vj(2)] = -1; row[vj(3)] = -1
    A.append(row); bc.append(-1 - MG); bt.append(F(0))
    if cell == 'alpha':
        row = [F(0)] * nv
        row[vs(nS)] = -1; row[vj(1)] = 1; row[vj(2)] = 1
        A.append(row); bc.append(F(0)); bt.append(F(0))          # s_{nS} >= J
        row = [F(0)] * nv
        row[IP] = 2; row[vj(1)] = -1; row[vj(2)] = -1
        A.append(row); bc.append(F(0)); bt.append(F(4))          # J >= 2p - 4t
    else:
        row = [F(0)] * nv
        row[vs(nS)] = 1; row[vj(1)] = -1; row[vj(2)] = -1
        A.append(row); bc.append(-MG); bt.append(F(0))           # s_{nS} < J
    return A, bc, bt, nv


def main():
    pf = open(OUT, 'w')
    tmesh = [0.313, 0.32, 0.325, 0.33, 1 / 3]
    stat = {}
    for cell in ['alpha', 'beta']:
        n_wit = n_reach = n_pack = n_canon = 0
        for m in range(6, 15):
            for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
                for k in range(2, m - 2):
                    A, bc, bt, nv = build(m, cnt, k, cell)
                    Af = np.array([[float(x) for x in row] for row in A])
                    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
                    nS = m - 1
                    rng = np.random.default_rng(m * 37 + k)
                    for t0 in tmesh:
                        for _ in range(2):
                            c = rng.standard_normal(nv)
                            res = linprog(c=c, A_ub=Af, b_ub=bcf + btf * t0, bounds=(None, None), method='highs')
                            if res.status != 0:
                                continue
                            x = res.x
                            p = x[0]; s = list(x[3:3 + nS]); j = list(x[3 + nS:3 + 2 * nS])
                            n_wit += 1
                            seq = sorted([p] + s, reverse=True) + sorted(j + [t0], reverse=True)
                            ev = fallback_event(seq, m)
                            if ev is not None:
                                n_reach += 1
                            pk = packs_into_m([p] + s + j + [t0], m)
                            if pk:
                                n_pack += 1
                                if cell == 'alpha':
                                    print(f"  **α' 可装箱! m={m} cnt={cnt} k={k} t={t0}", flush=True)
                                    print(f"    s={np.round(s,3)}\n    j={np.round(j,3)}", flush=True)
                            if cell == 'beta' and check_packing(s, j, t0):
                                n_canon += 1
                    print(f'  {cell} m={m} cnt={cnt[:3]} k={k} 完成（见证 {n_wit}）', flush=True)
        stat[cell] = (n_wit, n_reach, n_pack, n_canon)
        pf.write(json.dumps({'cell': cell, 'wit': n_wit, 'reach': n_reach,
                             'pack': n_pack, 'canon': n_canon}) + '\n')
        pf.flush()
        print(f"== {cell}: 见证 {n_wit} 可达 {n_reach} 可装箱 {n_pack} canonical {n_canon}", flush=True)


if __name__ == '__main__':
    main()
