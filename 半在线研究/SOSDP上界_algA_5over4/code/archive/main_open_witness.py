"""main_open_witness.py —— k<m−1 open 点的决定性实验：见证点可达性+可装箱性。
从 open 点（main_jjj_enum.jsonl tier=open）的存活 hi 区对出发，
取 LP（角落+挤压+SS01+对假设）原始可行点，实跑 Algorithm A（fallback_event 判可达），
可达者做 DFS 精确装箱判定。
判决含义：
  可达且可装箱 >0 ⟹ (P) 为假（与 proof.md T'' 冲突，警报）；
  可达但不可装箱 ⟹ 需匹配层证明；
  全不可达 ⟹ (P) 空虚成立，LP 路线需可达性约束（mon3 级动力学）。
断点：main_open_witness.jsonl。
"""
import numpy as np
from scipy.optimize import linprog
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
from main_jjj_enum import base_rows, pair_row, ss01_row
from main_reach_pack2 import packs_into_m
from toolbox import fallback_event

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_open_witness.jsonl')


def sample_witnesses(m, cnt, k, pairs, nsample, seed):
    R0, nv, nS = base_rows(m, cnt, k)
    R1 = R0 + [ss01_row(nv)]
    nS_ = nS
    pts = []
    rng = np.random.default_rng(seed)
    for (i, j) in pairs:
        R = R1 + [pair_row(nv, nS_, i, j)]
        Af = np.array([[float(x) for x in row] for row, _, _, _ in R])
        bcf = np.array([float(c0) for _, c0, _, _ in R])
        btf = np.array([float(c1) for _, _, c1, _ in R])
        A2 = Af.copy()
        A2[:, 1] -= btf
        for t0 in [0.30, 0.32, 1 / 3]:
            for _ in range(nsample):
                c = rng.standard_normal(nv)
                res = linprog(c=c, A_ub=np.vstack([A2, -np.eye(nv)[1]]),
                              b_ub=np.concatenate([bcf, [-t0]]), bounds=(None, None),
                              method='highs')
                if res.status == 0:
                    pts.append((i, j, res.x))
    return pts, nS


def main(mlo=8, mhi=14, nsample=2, maxpairs=3):
    recs = [json.loads(l) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_jjj_enum.jsonl'))]
    opens = [r for r in recs if r['tier'] == 'open' and mlo <= r['m'] <= mhi]
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            try:
                r = json.loads(l)
                done.add((r['m'], tuple(r['cnt']), r['k']))
            except Exception:
                pass
    pf = open(OUT, 'a')
    t0 = time.time()
    for r in opens:
        m, cnt, k = r['m'], tuple(r['cnt']), r['k']
        if (m, cnt, k) in done:
            continue
        pairs = [tuple(p) for p in r['feas_pairs']][:maxpairs]
        pts, nS = sample_witnesses(m, cnt, k, pairs, nsample, seed=m * 991 + k)
        tot = reach = rp = 0
        for (i, j, x) in pts:
            p, t = x[0], x[1]
            s = list(x[2:2 + nS])
            jj = list(x[2 + nS:2 + 2 * nS])
            seq = sorted([p] + s, reverse=True) + sorted(jj + [t], reverse=True)
            ev = fallback_event(seq, m)
            tot += 1
            if ev is None:
                continue
            reach += 1
            if packs_into_m([p] + s + jj + [t], m):
                rp += 1
                print(f"  **可达且可装箱** m={m} cnt={cnt} k={k} 对=({i},{j}) p={p:.3f} t={t:.3f}", flush=True)
        pf.write(json.dumps({'m': m, 'cnt': cnt, 'k': k, 'n': tot,
                             'reach': reach, 'reach_pack': rp}) + '\n')
        pf.flush()
        print(f"m={m} cnt={cnt[:3]} k={k}: 见证{tot} 可达{reach} 可达且可装箱{rp}（{time.time()-t0:.0f}s）", flush=True)
    print('见证实验结束')


if __name__ == '__main__':
    main()
