"""a3_cert115_clean.py —— uncond 115 点的干净精确证书（去 B4 + 去 A2）。
动机（agent-3 敌意复核）：main_cert154.jsonl noSJrev 档 111/115 支撑含 B4（threshold-Hall，
合法性一行论证有逃逸口，SUSPECT）；A2 0/308 支撑。浮点消融（a3_b4_ablate.py）：去 B4/A2
仍 154/154 INF ⟹ 可干净化。本脚本对 uncond 115 点重发**精确 Fraction t-uniform 证书**，
行集 = main noSJrev 档（去 SJrev/S1v/JJrev）再 去 B4、A2 —— 全行为已审合法行。
断点：a3_cert115_clean.jsonl。
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
import a1_value_lp2 as V
from main_cegar3 import MG
from fast_lp import float_cert_rows, exact_verify_support

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'a3_cert115_clean.jsonl')
CLEAN_KW = dict(use_sjrev=False, use_s1v=False, use_jjrev=False, use_b4=False, use_a2=False)


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
    pts = []
    for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main_ablation_class.jsonl')):
        r = json.loads(l)
        if r['cls'] == 'uncond':
            pts.append((r['m'], tuple(r['cnt']), r['k']))
    print(f'uncond 点 {len(pts)} 个')
    done = set()
    if os.path.exists(OUT):
        for l in open(OUT):
            try:
                r = json.loads(l); done.add((r['m'], tuple(r['cnt']), r['k']))
            except Exception:
                pass
    pf = open(OUT, 'a')
    t0 = time.time(); nok = nfail = 0
    for m, cnt, k in pts:
        if (m, cnt, k) in done:
            continue
        R, nv = build(m, list(cnt), k, CLEAN_KW)
        yf = float_cert_rows(R, nv)
        if yf is None:
            rec = {'m': m, 'cnt': list(cnt), 'k': k, 'status': 'FLOAT_NO_CERT'}
            nfail += 1
            print(f'  ✗ 浮点无证书 m={m} cnt={cnt} k={k}', flush=True)
        else:
            y, sup = exact_verify_support(R, nv, yf)
            if y is None:
                rec = {'m': m, 'cnt': list(cnt), 'k': k, 'status': 'RATFAIL'}
                nfail += 1
                print(f'  ✗ RATFAIL m={m} cnt={cnt} k={k}', flush=True)
            else:
                rec = {'m': m, 'cnt': list(cnt), 'k': k, 'status': 'OK',
                       'support': [R[i][3] for i in sup]}
                nok += 1
        pf.write(json.dumps(rec) + '\n'); pf.flush()
    pf.close()
    print(f'干净证书收官：OK {nok} FAIL {nfail}（{time.time()-t0:.0f}s）')


if __name__ == '__main__':
    main()
