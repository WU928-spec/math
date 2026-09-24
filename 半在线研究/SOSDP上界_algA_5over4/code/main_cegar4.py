"""main_cegar4.py —— CEGAR 第 4 轮：39 个 SJrev 承重点的去SJrev幻影解剖。
判决三分支：①幻影全非真角落 → 抽 A6 行候选；②出现真角落+可装箱 → G1 证伪（告警）；
③幻影样本都取不到（noSJrev LP 在该 t 网格本就不可行）→ 该点 t 覆盖需加密。
断点：main_cegar4.jsonl。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V
from main_cegar3 import MG
from main_phantom_corner import check_packing, assign_juniors

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_cegar4.jsonl')
TMESH = [0.27, 0.28, 0.29, 0.30, 0.31, 0.32, 0.33, 1 / 3]


def build_nosjrev(m, cnt, k):
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
    return A, bc, bt, nv


def sample(m, cnt, k, nwant=3, seed=11):
    A, bc, bt, nv = build_nosjrev(m, cnt, k)
    Af = np.array([[float(x) for x in row] for row in A])
    bcf = np.array([float(x) for x in bc]); btf = np.array([float(x) for x in bt])
    rng = np.random.default_rng(seed)
    pts = []
    for t0 in TMESH:
        for _ in range(30):
            c = rng.standard_normal(nv)
            r = linprog(c=c, A_ub=Af, b_ub=bcf + btf * t0, bounds=(None, None), method='highs')
            if r.status == 0:
                pts.append((t0, r.x))
                break
        if len(pts) >= nwant:
            break
    return pts


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    pts39 = [json.loads(l) for l in open(os.path.join(here, 'main_ablation_class.jsonl'))]
    pts39 = [r for r in pts39 if r['cls'] == 'sjrev']
    pf = open(OUT, 'w')
    n_real = n_ghost = n_nosample = 0
    for r in pts39:
        m, cnt, k = r['m'], tuple(r['cnt']), r['k']
        nS = m - 1
        pts = sample(m, cnt, k)
        if not pts:
            n_nosample += 1
            pf.write(json.dumps({'m': m, 'cnt': cnt, 'k': k, 'verdict': 'nosample'}) + '\n')
            print(f'm={m} cnt={cnt[:3]} k={k}: 无幻影样本（t 网格加密待查）', flush=True)
            continue
        real = None
        reasons = []
        for (t0, x) in pts:
            p, am, q1 = x[0], x[1], x[2]
            s = list(x[3:3 + nS]); j = list(x[3 + nS:3 + 2 * nS])
            pack = check_packing(s, j, t0)
            ok, kk, assign, reason = assign_juniors(s, j, p, t0, am, q1)
            reasons.append(reason)
            if ok and pack:
                real = (t0, p, am, q1)
                break
        if real:
            n_real += 1
            verdict = 'REAL+PACK（G1 证伪告警！）'
        else:
            n_ghost += 1
            verdict = 'ghost'
        pf.write(json.dumps({'m': m, 'cnt': cnt, 'k': k, 'verdict': verdict, 'reasons': reasons}) + '\n')
        pf.flush()
        if real or len(reasons) < 2:
            print(f'm={m} cnt={cnt[:3]} k={k}: {verdict} {reasons[0][:90]}', flush=True)
    print(f'\n判决：ghost {n_ghost}（可抽 A6）/ REAL {n_real}（G1 证伪）/ nosample {n_nosample}')


if __name__ == '__main__':
    main()
