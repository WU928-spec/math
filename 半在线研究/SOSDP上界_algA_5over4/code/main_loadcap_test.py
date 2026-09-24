"""main_ 负载帽行实测：4s_i+4j_i<=5a_m+5q_1（角落合法：非 M0 机负载恒<=K=5L/4）
加进 base 后重测 main_jjj_enum.jsonl 的 264 个 open 点（存活对是否死亡）。
负载帽合法性与已审计 sk+q1<=K（机器 jj）同型——每台非 M0 机负载 in (p, K]。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
from main_jjj_enum import base_rows, pair_row, ss01_row
from fast_lp import float_cert_rows, exact_verify_support

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_loadcap_test.jsonl')


def loadcap_rows(nv, nS):
    rows = []
    for i in range(nS):
        row = [0.0] * nv
        row[2 + i] = 4.0
        row[2 + nS + i] = 4.0
        row[2 + 2 * nS] = -5.0
        row[2 + 2 * nS + 1] = -5.0
        rows.append((row, F(0), F(0), f'cap{i}'))
    return rows


def lp_inf(R, nv):
    yf = float_cert_rows(R, nv)
    if yf is None:
        return False, False
    y, sup = exact_verify_support(R, nv, yf)
    return (y is not None), (y is None)


def main():
    recs = [json.loads(l) for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_jjj_enum.jsonl'))]
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
        R0 = R0 + loadcap_rows(nv, nS)
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
        if tier == 'open':
            print(f'  仍 open: m={m} cnt={cnt} k={k} 存活 {feas[:6]}', flush=True)
    print(f'负载帽复测结束 {stat}（{time.time()-t0:.0f}s）')


if __name__ == '__main__':
    main()
