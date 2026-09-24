"""main_band_test.py —— 值带合法行实测（c=1  razor cnt 专用）：
V1: s_{nS-2}+t<=1（第二大 senior<=1-t：>1-t 的 senior 无件可配必独占 c 箱，c=1 至多一个）。
对 main_jjj_enum.jsonl 的 264 个 open 点，在 base+V1 下重测存活对（Tier1/Tier2 语义同前）。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
from main_jjj_enum import base_rows, pair_row, ss01_row
from fast_lp import float_cert_rows, exact_verify_support

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_band_test.jsonl')


def v1_row(nv, nS):
    row = [0.0] * nv
    row[2 + nS - 2] = 1.0
    row[1] = 1.0
    return (row, F(1), F(0), 'smax2+t<=1')


def lp_inf(R, nv):
    yf = float_cert_rows(R, nv)
    if yf is None:
        return False, False
    y, sup = exact_verify_support(R, nv, yf)
    return (y is not None), (y is None)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    recs = [json.loads(l) for l in open(os.path.join(here, 'main_jjj_enum.jsonl'))]
    opens = [r for r in recs if r['tier'] == 'open']
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
    stat = {'closed1': 0, 'closed2': 0, 'open': 0}
    for r in opens:
        m, cnt, k = r['m'], tuple(r['cnt']), r['k']
        if (m, cnt, k) in done:
            continue
        R0, nv, nS = base_rows(m, cnt, k)
        R0 = R0 + [v1_row(nv, nS)]
        surv = [tuple(p) for p in r['feas_pairs']]
        feas, nrat = [], 0
        for (i, j) in surv:
            inf, rat = lp_inf(R0 + [pair_row(nv, nS, i, j)], nv)
            nrat += rat
            if not inf and not rat:
                feas.append((i, j))
        if not feas:
            tier = 'closed1'
        else:
            R1 = R0 + [ss01_row(nv)]
            feas2 = []
            for (i, j) in feas:
                inf, rat = lp_inf(R1 + [pair_row(nv, nS, i, j)], nv)
                nrat += rat
                if not inf and not rat:
                    feas2.append((i, j))
            tier = 'open' if feas2 else 'closed2'
            feas = feas2
        stat[tier] += 1
        pf.write(json.dumps({'m': m, 'cnt': cnt, 'k': k, 'tier': tier,
                             'feas_pairs': feas, 'ratfail': nrat}) + '\n')
        pf.flush()
        if tier != 'open':
            pass
    print(f'V1(s_2nd+t<=1) 复测结束 {stat}（{time.time()-t0:.0f}s）')


if __name__ == '__main__':
    main()
