"""main_cert154.py —— open 段 154 点全量精确 t-uniform Farkas 证书（Fraction）。
两档：full 行集（154 点）+ noSJrev 行集（115 点无条件档）。断点：main_cert154.jsonl。"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V
from main_cegar3 import MG
from fast_lp import float_cert_rows, exact_verify_support

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_cert154.jsonl')

def build(m, cnt, k, kw):
    nS = m - 1
    A, bc, bt, names, leg, nv = V.build(m, cnt, **kw)
    A, bc, bt, names = list(A), list(bc), list(bt), list(names)
    IP, IAM, IQ1 = 0, 1, 2
    vs = lambda r: 3 + (r - 1); vj = lambda r: 3 + nS + (r - 1)
    for i in range(1, k + 1):
        row = [F(0)] * nv; row[IP] = 1; row[vs(i)] = -1; row[vj(nS - k + i)] = -1
        A.append(row); bc.append(-MG); bt.append(F(0)); names.append(f'A5_{i}')
    row = [F(0)] * nv; row[vs(k)] = 4; row[IAM] = -5; row[IQ1] = -1
    A.append(row); bc.append(F(0)); bt.append(F(0)); names.append('LZ')
    if k < nS:
        row = [F(0)] * nv; row[vs(k + 1)] = -4; row[IAM] = 5; row[IQ1] = 1
        A.append(row); bc.append(-MG); bt.append(F(0)); names.append('HZ')
    R = [([float(x) for x in row], bc[i], bt[i], names[i]) for i, row in enumerate(A)]
    return R, nv

def main():
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            try:
                r = json.loads(l); done.add((r['m'], tuple(r['cnt']), r['k'], r['tier']))
            except Exception: pass
    pf = open(OUT, 'a')
    t0 = time.time(); nok = nfail = 0
    for m in range(6, 17):
        for cnt in [(1, m - 3, 0, 1, 0, 0), (2, m - 5, 0, 1, 1, 0)]:
            for k in range(2, m - 2):
                for tier, kw in [('full', {}), ('noSJrev', dict(use_sjrev=False, use_s1v=False, use_jjrev=False))]:
                    if (m, cnt, k, tier) in done: continue
                    R, nv = build(m, cnt, k, kw)
                    yf = float_cert_rows(R, nv)
                    if yf is None:
                        rec = {'m': m, 'cnt': cnt, 'k': k, 'tier': tier, 'status': 'FLOAT_NO_CERT'}
                        nfail += 1
                        print(f'  ✗ 浮点无证书 m={m} cnt={cnt} k={k} {tier}', flush=True)
                    else:
                        y, sup = exact_verify_support(R, nv, yf)
                        if y is None:
                            rec = {'m': m, 'cnt': cnt, 'k': k, 'tier': tier, 'status': 'RATFAIL'}
                            nfail += 1
                            print(f'  ✗ RATFAIL m={m} cnt={cnt} k={k} {tier}', flush=True)
                        else:
                            rec = {'m': m, 'cnt': cnt, 'k': k, 'tier': tier, 'status': 'OK',
                                   'support': [R[i][3] for i in sup]}
                            nok += 1
                    pf.write(json.dumps(rec) + '\n'); pf.flush()
        print(f'm={m} 完成（{time.time()-t0:.0f}s，OK {nok} FAIL {nfail}）', flush=True)
    print(f'证书补扫收官：OK {nok} FAIL {nfail}')

if __name__ == '__main__':
    main()
